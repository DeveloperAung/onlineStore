from django.contrib import messages
from django.shortcuts import render, redirect

from common.utlis import return_page_objs
from .forms import AddCategoryForm
from . models import Category


def list_category(request):
    categories = Category.objects.all()
    categories, query_string = return_page_objs(request, categories)
    context = {
        'page_objs': categories,
        'query_string': query_string
    }
    return render(request, 'store/setup/category/listCategory.html', context)


def add_category(request):

    if request.method == "POST":
        form = AddCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'New category name added!')
            return redirect('list_category')
    else:
        form = AddCategoryForm
    return render(request, 'store/setup/category/addCategory.html', {'form': form})

