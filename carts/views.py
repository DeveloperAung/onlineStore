from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect

from carts.models import CartItem, Cart
from orders.models import PaymentMethod, Order
from store.models import Product


def _cart_id(request):
    cart_id = request.session.get('shopping_cart_id')
    if request.user.is_authenticated:
        shopping_cart = Cart.objects.filter(created_by=request.user).first()
        request.session['shopping_cart_id'] = str(shopping_cart.cart_id) if shopping_cart else None
    return cart_id


def _order_uuid(request):
    order_uuid = request.session.get('order_uuid')
    if request.user.is_authenticated:
        order = Order.objects.filter(
            is_active=True, is_ordered=False, user_id=request.user
        ).order_by('created_date').last()
        request.session['order_uuid'] = str(order.uuid) if order else None
    return order_uuid


def create_cart(request, cart_id):
    if cart_id:
        shopping_cart, created = Cart.objects.get_or_create(cart_id=cart_id)
        if created:
            request.session['shopping_cart_id'] = str(shopping_cart.cart_id)
    else:
        shopping_cart = Cart.objects.create()
        shopping_cart.save()
        request.session['shopping_cart_id'] = str(shopping_cart.cart_id)
    return shopping_cart


def calculate_tax(total):
    tax = total * 0.09
    return round(tax, 2), round(total + tax, 2)


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)    # get the product
    cart_id = _cart_id(request)
    available_qty = product.get_qty()['available_qty']
    shopping_cart = create_cart(request, cart_id)

    # If the user is authenticated
    if current_user.is_authenticated:
        if request.method == 'POST':
            qty = request.POST.get('qty')

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user, cart=shopping_cart).exists()
        if is_cart_item_exists:
            # print('shopping_cart', shopping_cart)
            cart_item = CartItem.objects.get(product=product, cart=shopping_cart)

            if available_qty:
                if int(qty) + 1 > available_qty:
                    cart_item.quantity = available_qty
                    messages.warning(request, f'The product {cart_item.product.product_name} max order is {available_qty}')
                else:
                    cart_item.quantity = int(qty) + 1 if qty else cart_item.quantity + 1
                cart_item.save()
            else:
                CartItem.objects.filter(id=cart_item.id).delete()
                messages.warning(request, 'Product out of stock!')
        else:
            if available_qty > 0:
                cart_item = CartItem.objects.create(product=product, cart=shopping_cart, quantity=1, user=current_user)
                cart_item.save()
            else:
                messages.warning(request, 'Product out of stock!')
        return redirect('cart')
    # If the user is not authenticated
    else:
        if request.method == 'POST':
            qty = request.POST.get('qty')

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=shopping_cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.get(product=product, cart=shopping_cart)
            cart_item.quantity = int(qty) + 1 if qty else cart_item.quantity + 1
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product, cart=shopping_cart)
            cart_item.save()
        return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            shopping_cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=shopping_cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except Exception as e:
        print('error', e)
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        shopping_cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=shopping_cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(cart__cart_id=_cart_id(request), is_active=True)
        else:
            shopping_cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=shopping_cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax, grand_total = calculate_tax(total)
    except ObjectDoesNotExist:
        pass  # just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)


def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(cart__cart_id=_cart_id(request), is_active=True)
        else:
            shopping_cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=shopping_cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax, grand_total = calculate_tax(total)

        order_uuid = _order_uuid(request)
        if order_uuid:
            order = Order.objects.get(is_ordered=False, uuid=order_uuid, is_active=True)
            payment_methods = PaymentMethod.objects.filter(is_active=True, type=order.order_type)

            delivery_fee = None
            if order.order_type == 'deli':
                delivery_fee = payment_methods.first().delivery_amount
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'delivery_fee': delivery_fee,
                'grand_total': grand_total + delivery_fee if delivery_fee else 0,
                'payment_methods': payment_methods
            }
            if order:
                return render(request, 'orders/payments.html', context)
    except ObjectDoesNotExist:
        print('error checkout')
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)
