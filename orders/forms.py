from django import forms
from .models import Order, DeliveryAddress


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_type', 'order_note', 'full_name', 'phone', 'email']


class OrderDeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['address_line_1', 'address_line_2', 'postal_code', 'unit', 'floor']
