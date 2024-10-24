from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect

from carts.models import CartItem, Cart
from store.models import Product


def _cart_id(request):
    cart_id = request.session.get('shopping_cart_id')
    return cart_id


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
    return total * 0.02


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)    # get the product
    cart_id = _cart_id(request)
    shopping_cart = create_cart(request, cart_id)

    # If the user is authenticated
    if current_user.is_authenticated:
        if request.method == 'POST':
            qty = request.POST.get('qty')

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user, cart=shopping_cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.get(product=product, cart=shopping_cart)
            cart_item.quantity = int(qty) + 1 if qty else cart_item.quantity + 1
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product, cart=shopping_cart, quantity=1, user=current_user)
            cart_item.save()
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
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            shopping_cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=shopping_cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = calculate_tax(total)
        grand_total = total + tax
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
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            shopping_cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=shopping_cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = calculate_tax(total)
        grand_total = total + tax
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
