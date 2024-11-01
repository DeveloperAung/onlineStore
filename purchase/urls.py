from django.urls import path
from . import views


urlpatterns = [
    path('', views.purchase_main, name='purchase_main'),

    path('add_purchase', views.create_purchase_invoice, name='create_purchase_invoice'),
    path('complete_purchase/id?=<uuid:purchase_uuid>', views.complete_purchase, name='complete_purchase'),
    path('form_purchase/id?=<uuid:purchase_uuid>', views.form_purchase, name='form_purchase'),
    path('add_purchase_items/id?=<uuid:purchase_uuid>', views.add_purchase_items, name='add_purchase_items'),
    path('remove_purchase_items/details_id?=<int:details_id>', views.remove_purchase_items, name='remove_purchase_items'),

]
