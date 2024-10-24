from django import forms
from .models import Category


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'slug', 'description', 'cat_image']

    def __init__(self, *args, **kwargs):
        super(AddCategoryForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': '4'})
        self.fields['cat_image'].widget = forms.FileInput(attrs={'class': 'form-control'})
