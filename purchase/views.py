from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from common.utlis import return_page_objs
from store.models import Product
from .forms import CreatePurchaseInvoiceForm, AddPurchaseProductsForm
from .models import Purchase, PurchaseProduct


purchase_status = {
    'created': 7,
    'in_progress': 8,
    'completed': 9
}


def purchase_main(request):
    form_create_invoice = CreatePurchaseInvoiceForm
    purchased_invoices = Purchase.objects.filter(is_active=True)
    purchased_invoices, query_string = return_page_objs(request, purchased_invoices)
    context = {
        'form_create_invoice': form_create_invoice,
        'page_objs': purchased_invoices,
    }
    return render(request, 'purchase/listPurchase.html', context)


def create_purchase_invoice(request):
    if request.method == 'POST':
        form = CreatePurchaseInvoiceForm(request.POST)
        if form.is_valid():
            form_created = form.save()
            form_created.status_id = purchase_status['created']
            form_created.save()
            return redirect('form_purchase', form_created.uuid)
        else:
            messages.warning(request, 'Please fill correct information!')

    return redirect('purchase_main')
    # HttpResponse('Something went wrong purchase invoice creation!')


def form_purchase(request, purchase_uuid):
    purchase_invoice = Purchase.objects.prefetch_related(
        Prefetch(
            'purchase_products',  # This should now work with the corrected related_name
            queryset=PurchaseProduct.objects.filter(is_active=True)
        )
    ).get(uuid=purchase_uuid)

    purchase_products = purchase_invoice.purchase_products.all()
    total = 0
    for product in purchase_products:
        total += product.purchase_qty * product.product_price

    shipping_fee = purchase_invoice.shipping_fee if purchase_invoice.shipping_fee else 0
    delivery_fee = purchase_invoice.delivery_fee if purchase_invoice.delivery_fee else 0
    context = {
        'purchase_invoice': purchase_invoice,
        'products': Product.objects.filter(is_active=True),
        'total': total,
        'grand_total': total + shipping_fee + delivery_fee
    }
    return render(request, 'purchase/formPurchase.html', context)


@login_required(login_url='login')
def add_purchase_items(request, purchase_uuid):
    if request.method == "POST":
        form = AddPurchaseProductsForm(request.POST)
        purchase_invoice = get_object_or_404(Purchase, uuid=purchase_uuid)
        if form.is_valid():
            product = form.cleaned_data['product']
            qty = form.cleaned_data['purchase_qty']
            expiry_date = form.cleaned_data['expiry_date']
            try:
                is_item_exists = PurchaseProduct.objects.get(
                    product=product, expiry_date=expiry_date, purchase_order=purchase_invoice)
                is_item_exists.purchase_qty += 1
                is_item_exists.available_qty = is_item_exists.purchase_qty
                is_item_exists.balance_qty = is_item_exists.purchase_qty
                if not is_item_exists.is_active:
                    is_item_exists.is_active = True
                is_item_exists.save()
            except PurchaseProduct.DoesNotExist:
                data = PurchaseProduct()
                data.purchase_order = purchase_invoice
                data.product = product
                data.purchase_qty = qty
                data.available_qty = data.purchase_qty
                data.balance_qty = data.purchase_qty
                data.product_price = float(form.cleaned_data['product_price'])
                data.expiry_date = expiry_date
                data.save()
                if purchase_invoice.status.internal_status == 'Created':
                    purchase_invoice.status_id = purchase_status['in_progress']
                    purchase_invoice.save()
        else:
            for field in form:
                for error in field.errors:
                    messages.warning(request, f'{ field.name } - {error }')
    return redirect('form_purchase', purchase_uuid)


@login_required(login_url='login')
def remove_purchase_items(request, details_id):
    product = PurchaseProduct.objects.get(id=details_id)
    purchase_uuid = product.purchase_order.uuid
    product.purchase_qty -= 1
    product.available_qty = product.purchase_qty
    product.balance_qty = product.purchase_qty
    if product.purchase_qty < 1:
        product.is_active = False
    product.save()
    return redirect('form_purchase', purchase_uuid)


@login_required(login_url='login')
def complete_purchase(request, purchase_uuid):
    purchase_invoice = get_object_or_404(Purchase, uuid=purchase_uuid)
    if purchase_invoice.get_items_count()['total_items'] > 0:
        purchase_invoice.status_id = purchase_status['completed']
        purchase_invoice.save()
        return redirect('purchase_main')
    else:
        messages.warning(request, "Please add item to complete the purchase!")
        return redirect('form_purchase', purchase_invoice.uuid)



