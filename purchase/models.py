import uuid as uuid

from django.db.models import Sum

from common.models import BaseModel, Status
from django.db import models
import uuid

from store.models import Product


class Purchase(BaseModel):
    uuid = models.UUIDField(editable=False, unique=True, default=uuid.uuid4)
    purchase_date = models.DateTimeField()
    invoice_no = models.CharField(max_length=25)
    order_total = models.FloatField(default=0)
    shipping_fee = models.FloatField(default=0)
    delivery_fee = models.FloatField(default=0)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, blank=True, null=True)
    is_purchased = models.BooleanField(default=False)

    def get_items_count(self):
        # Retrieve all related PurchaseProduct instances
        purchase_products = self.purchase_products.filter(is_active=True)

        # Total number of unique products
        total_items = purchase_products.values('product').distinct().count()

        # Total quantity of all products
        total_qty = purchase_products.aggregate(total_qty=Sum('purchase_qty'))['total_qty'] or 0

        return {'total_items': total_items, 'total_qty': total_qty}

    def get_amount(self):
        purchase_products = self.purchase_products.filter(is_active=True)
        total = 0
        for product in purchase_products:
            total += product.purchase_qty * product.product_price
        shipping_fee = self.shipping_fee if self.shipping_fee else 0
        delivery_fee = self.delivery_fee if self.delivery_fee else 0
        grand_total = shipping_fee + delivery_fee
        return {'total': total, 'grand_total': grand_total}

    def __str__(self):
        return {self.order_number}


class PurchaseProduct(BaseModel):
    purchase_order = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='purchase_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_products')
    purchase_qty = models.FloatField()
    balance_qty = models.FloatField()       # is in cart but have not made payment yet
    available_qty = models.FloatField()     # available qty to order by customer
    product_price = models.FloatField()
    expiry_date = models.DateTimeField(blank=True, null=True)

    def sub_total(self):
        return self.product.price * self.purchase_qty

    def __str__(self):
        return f'{self.purchase_order} - {self.product.product_name}'
