from django.urls import path
from . import views


urlpatterns = [
    path('', views.store, name='store'),

    path('setup', views.setup_main, name='setup_main'),
    path('setup/product/list', views.list_product, name='list_product'),
    path('setup/product/add', views.add_product, name='add_product'),
    path('product/<slug:category_slug>/<slug:product_slug>/', views.details_product, name='details_product'),

    path('search/', views.search, name='search'),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('brand/<slug:brand_slug>/', views.store, name='products_by_brand'),
]
