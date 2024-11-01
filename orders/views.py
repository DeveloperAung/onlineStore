from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from carts.models import CartItem
from carts.views import _cart_id, _order_uuid, calculate_tax
from purchase.models import PurchaseProduct
from .forms import OrderForm, OrderDeliveryAddressForm
import datetime
from .models import Order, Payment, OrderProduct, DeliveryAddress, PaymentMethod, OrderLine
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import hashlib
import hmac
import requests
from django.conf import settings


status_order_id = {
    'ordered': 1
}


def get_deli_fee(order):
    deli_fee = 0
    try:
        deli_fee = order.payment.payment_method.delivery_amount
    except AttributeError:
        pass
    return deli_fee


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/orderReceivedEmail.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.content_subtype = 'html'
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def paid_order(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        if order.is_ordered:
            return redirect('order_complete', order.payment.id, order.order_number)
    except Order.DoesNotExist:
        messages.error(request, "Sorry your order number not exist!")
        return redirect('store')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        tax, grand_total = calculate_tax(order.order_total)
        amount_paid = grand_total + get_deli_fee(order)
        payment = Payment(
            user=request.user if request.user.is_authenticated else None,
            payment_id=order.order_number,
            payment_method_id=payment_method,
            amount_paid=amount_paid,
            status='Paid',
        )
        payment.save()

        order.payment = payment
        order.delivery_fee = get_deli_fee(order)
        order.is_ordered = True
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(cart__cart_id=_cart_id(request))

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.payment = payment
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.save()

            # Reduce the quantity of the sold products
            order_qty = item.quantity
            available_qty = item.product.get_qty()['available_qty']

            while available_qty >= order_qty > 0:
                product = PurchaseProduct.objects.filter(is_active=True, available_qty__gt=0).order_by(
                    'expiry_date').first()

                if not product:
                    messages.warning(
                        request, f'Sorry! Product {item.product.product_name} currently out of stock. Removed from your cart')
                    break

                if product.available_qty >= order_qty:
                    product.available_qty -= order_qty
                    product.save()
                    OrderLine.objects.create(order_product=orderproduct, purchase_product=product, qty=order_qty)
                    order_qty = 0  # Order fulfilled

                else:
                    # If product does not have enough quantity, reduce only available quantity
                    order_qty -= product.available_qty
                    OrderLine.objects.create(order_product=orderproduct, purchase_product=product,
                                             qty=product.available_qty)
                    product.available_qty = 0
                    product.save()

                available_qty = item.product.get_qty()['available_qty']

            else:
                CartItem.objects.filter(id=item.id).delete()
                messages.warning(request,
                                 f'Sorry! Product {item.product.product_name} currently out of stock. Removed from your cart')

            # product = Product.objects.get(id=item.product_id)
            # product.stock -= item.quantity
            # product.save()

        # Clear cart
        CartItem.objects.filter(cart__cart_id=_cart_id(request)).delete()

        # Send order recieved email to customer
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/orderReceivedEmail.html', {
            'user': request.user,
            'order': order,
            'ordered_products': OrderProduct.objects.filter(is_active=True, order=order),
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': order.order_total,
            'grand_total': order.order_total + order.tax + order.delivery_fee
        })
        to_email = order.email
        # to_email.append(request.user.email) if request.user.is_authenticated else None

        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.content_subtype = 'html'
        send_email.send()
        return redirect('order_complete', payment.id, order.order_number)
    else:
        return redirect('place_order')


@csrf_exempt
def update_payment_method(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_method_id = data.get('payment_method_id')
        # order_uuid = data.get('orderUUID')
        # order = Order.objects.get(uuid=order_uuid)
        payment_method = PaymentMethod.objects.get(id=payment_method_id)
        # order.delivery_fee = payment_method.delivery_amount
        # order.save()
        return JsonResponse({
            'success': True,
            'deli_fee': payment_method.delivery_amount,
            'desc': payment_method.description
        })
    return JsonResponse({'success': False})


def place_order(request, total=0, quantity=0,):
    current_user = request.user
    cart_id = _cart_id(request)

    cart_items = CartItem.objects.filter(cart__cart_id=cart_id)

    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')

    total = 0
    for cart_item in cart_items:
        available_qty = cart_item.product.get_qty()['available_qty']
        order_qty = cart_item.quantity
        if available_qty < order_qty > 0:
            cart_item.quantity = available_qty
            cart_item.save()
            messages.warning(request, f'We do not have enough stock for {cart_item.product.product_name}'  
                                      'and set item quota! Sorry for inconvenience cause!')
        elif available_qty < 1:
            CartItem.objects.filter(id=cart_item.id).delete()
            messages.warning(request, f'Product {cart_item.product.product_name} out of stock & removed.'
                                      'Sorry for inconvenience cause!')

        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax, grand_total = calculate_tax(total)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        from_address = OrderDeliveryAddressForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.cart_id = cart_id
            data.user = current_user if current_user.is_authenticated else None
            data.full_name = form.cleaned_data['full_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.order_note = form.cleaned_data['order_note']
            data.order_type = form.cleaned_data['order_type']
            data.order_total = total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.status_id = status_order_id['ordered']

            if data.order_type and data.order_type == 'deli':
                if from_address.is_valid():
                    data_address = DeliveryAddress()
                    data_address.address_line_1 = from_address.cleaned_data['address_line_1']
                    data_address.address_line_2 = from_address.cleaned_data['address_line_2']
                    data_address.postal_code = from_address.cleaned_data['postal_code']
                    data_address.unit = from_address.cleaned_data['unit']
                    data_address.floor = from_address.cleaned_data['floor']
                    data_address.save()

                    data.delivery_address = data_address
                else:
                    return redirect('checkout')
            # Generate order number
            data.save()
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")     #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            request.session['order_uuid'] = str(data.uuid)

            order = Order.objects.get(is_ordered=False, order_number=order_number, is_active=True)

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total + get_deli_fee(order),
                'payment_methods': PaymentMethod.objects.filter(is_active=True, type=order.order_type)
            }
            return render(request, 'orders/payments.html', context)
    else:
        order_uuid = _order_uuid(request)
        if order_uuid:
            try:
                order = Order.objects.get(is_ordered=False, uuid=order_uuid, is_active=True)
                context = {
                    'order': order,
                    'cart_items': cart_items,
                    'total': total,
                    'tax': tax,
                    'grand_total': grand_total,
                    'payment_methods': PaymentMethod.objects.filter(is_active=True, type=order.order_type)
                }
                if order:
                    return render(request, 'orders/payments.html', context)
            except Order.DoesNotExist:
                pass
        return redirect('checkout')


def order_complete(request, payment_id, order_number):

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(id=payment_id)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            'grand_total': subtotal + order.tax + order.delivery_fee
        }
        return render(request, 'orders/orderComplete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')


def create_payment(amount, currency="SGD", redirect_url="order_complete"):
    url = f"{settings.HITPAY_ENDPOINT}/payment-requests"
    headers = {"X-BUSINESS-API-KEY": settings.HITPAY_API_KEY}
    payload = {
        "amount": amount,
        "currency": currency,
        "redirect_url": redirect_url,
        "webhook": "your_webhook_url"  # Optional: Set up a webhook to listen for status updates
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json() if response.status_code == 200 else None
