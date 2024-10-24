from django.db import models

from common.models import BaseModel
from core.models import User
from store.models import Product
import uuid


class Cart(BaseModel):
    cart_id = models.UUIDField(editable=False, unique=True, default=uuid.uuid4)

    def __str__(self):
        return self.cart_id


class CartItem(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.FloatField(default=1)
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __unicode__(self):
        return self.product
