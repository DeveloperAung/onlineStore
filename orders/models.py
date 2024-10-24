from django.db import models
from core.models import User
from common.models import Status, BaseModel
from store.models import Product


class DeliveryAddress(BaseModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    unit = models.CharField(max_length=2, blank=True, null=True)
    floor = models.CharField(max_length=2, blank=True, null=True)
    postal_code = models.CharField(max_length=50)

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return f'{self.postal_code}'


class PaymentMethod(BaseModel):
    code = models.CharField(max_length=2)
    payment_method = models.CharField(max_length=150)

    def __str__(self):
        return self.payment_method


class Payment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.DO_NOTHING)
    amount_paid = models.CharField(max_length=100)  # this is the total amount paid
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.payment_id


class Order(BaseModel):
    ORDER_TYPE = (
        ('deli', 'Delivery'),
        ('col', 'Self Collect')
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name='order_status')
    order_type = models.CharField(ORDER_TYPE, default='deli', max_length=20)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.DO_NOTHING, related_name='order_address',
                                         blank=True, null=True)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=50)
    order_number = models.CharField(max_length=20)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.full_name} - {self.order_number}'


class OrderProduct(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.FloatField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.product.product_name
