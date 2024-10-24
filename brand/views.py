from django.contrib import messages
from django.shortcuts import render, redirect

from common.utlis import return_page_objs
from .forms import AddBrandForm
from .models import Brand


def list_brand(request):
    categories = Brand.objects.all()
    categories, query_string = return_page_objs(request, categories)
    context = {
        'page_objs': categories,
        'query_string': query_string
    }
    return render(request, 'store/setup/brand/listBrand.html', context)


def add_brand(request):
    if request.method == "POST":
        form = AddBrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'New brand name added!')
            return redirect('list_brand')
    else:
        form = AddBrandForm
    return render(request, 'store/setup/brand/addBrand.html', {'form': form})
