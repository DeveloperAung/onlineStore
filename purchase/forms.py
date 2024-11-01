from django import forms
from .models import Purchase, PurchaseProduct


class CreatePurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['purchase_date', 'invoice_no']

    def __init__(self, *args, **kwargs):
        super(CreatePurchaseInvoiceForm, self).__init__(*args, **kwargs)

        self.fields['purchase_date'].widget = forms.TextInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['invoice_no'].widget = forms.TextInput(attrs={'class': 'form-control'})


class AddPurchaseProductsForm(forms.ModelForm):
    class Meta:
        model = PurchaseProduct
        fields = ['product', 'purchase_qty', 'product_price', 'expiry_date']
