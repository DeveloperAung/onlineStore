from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from brand.models import Brand
from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from common.utlis import return_page_objs
from store.forms import AddProductForm, AddProductGalleryForm
from store.models import ProductGallery, Product


def setup_main(request):
    return render(request, 'store/setup/storeMain.html')


def store(request, category_slug=None, brand_slug=None):
    categories = None
    products = None

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True, is_active=True)
        products, query_string = return_page_objs(request, products)
    elif brand_slug is not None:
        brands = get_object_or_404(Brand, slug=brand_slug)
        products = Product.objects.filter(brand=brands, is_available=True, is_active=True)
        products, query_string = return_page_objs(request, products)
    else:
        products = Product.objects.all().filter(is_available=True, is_active=True).order_by('id')
        products, query_string = return_page_objs(request, products)

    context = {
        'page_objs': products,
        'query_string': query_string,
    }
    return render(request, 'store/store.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(is_active=True, is_available=True),
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
        else:
            products = Product.objects.filter(is_active=True, is_available=True).order_by('-created_date')
    else:
        products = Product.objects.filter(is_active=True, is_available=True).order_by('-created_date')

    product_count = products.count()
    products, query_string = return_page_objs(request, products)
    context = {
        'page_objs': products,
        'product_count': product_count,
        'query_string': query_string
    }
    return render(request, 'store/store.html', context)


def list_product(request):
    products = Product.objects.all()
    products, query_string = return_page_objs(request, products)
    context = {
        'page_objs': products,
        'query_string': query_string
    }
    return render(request, 'store/setup/product/listProduct.html', context)


def details_product(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    # if request.user.is_authenticated:
    #     try:
    #         orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
    #     except OrderProduct.DoesNotExist:
    #         orderproduct = None
    # else:
    #     orderproduct = None

    # Get the reviews
    # reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        # 'orderproduct': orderproduct,
        # 'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/setup/product/detailsProduct.html', context)


def add_product(request):

    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        form_gallery = AddProductGalleryForm(request.POST, request.FILES)
        files = request.FILES.getlist('image')
        if form.is_valid() and form_gallery.is_valid():
            # print('is_available', form.is_available)
            # print('is_use', form.is_use_low_stock)
            product = form.save()
            for f in files:
                print('file', f)
                ProductGallery.objects.create(product=product, image=f)
            messages.success(request, 'New Product has been added!')
            return redirect('list_product')
        else:
            messages.warning(request, "Please correct the errors!")
    else:
        form = AddProductForm
        form_gallery = AddProductGalleryForm()
    return render(request, 'store/setup/product/addProduct.html', {'form': form, 'form_gallery': form_gallery})




