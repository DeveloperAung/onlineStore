from django import forms
from .models import Brand


class AddBrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['brand_name', 'slug', 'description', 'brand_logo']

    def __init__(self, *args, **kwargs):
        super(AddBrandForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': '4'})
        self.fields['brand_logo'].widget = forms.FileInput(attrs={'class': 'form-control'})
