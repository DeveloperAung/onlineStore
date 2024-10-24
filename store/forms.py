from django import forms
from .models import Product, ProductGallery


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['code', 'product_name', 'slug', 'category', 'brand', 'description', 'price', 'low_lvl_stock',
                  'is_use_low_stock', 'is_available', 'images']

    def __init__(self, *args, **kwargs):
        super(AddProductForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['is_use_low_stock'].widget = forms.TextInput(attrs={'type': 'checkbox'})
        self.fields['is_available'].widget = forms.TextInput(attrs={'type': 'checkbox'})
        # widgets = {
        #     'is_use_low_stock': forms.TextInput(attrs={'type': 'checkbox'}),
        #     'is_available': forms.TextInput(attrs={'type': 'checkbox'}),
        #     'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '4'}),
        #     'images': forms.FileInput(attrs={'class': 'form-control'})
        # }


class AddProductGalleryForm(forms.ModelForm):
    # image = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model = ProductGallery
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super(AddProductGalleryForm, self).__init__(*args, **kwargs)

        self.fields['image'].widget = forms.FileInput(attrs={'class': 'form-control',
                                                             'accept': "image/png, image/gif, image/jpeg"})

