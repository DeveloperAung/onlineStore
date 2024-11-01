from django.urls import path
from . import views


urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),

    path('paid_order/order_no?=<str:order_number>', views.paid_order, name='paid_order'),

    path('payments/', views.payments, name='payments'),
    path('update_payment_method/', views.update_payment_method, name='update_payment_method'),
    path('order_complete/<int:payment_id>/<str:order_number>', views.order_complete, name='order_complete'),
]
