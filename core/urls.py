from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('my_account/', views.my_account, name='my_account'),
    path('c/dashboard', views.cus_dashboard, name='cus_dashboard'),
    path('s/dashboard', views.staff_dashboard, name='staff_dashboard'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotPassword/', views.forgot_password, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('change_password/', views.change_password, name='change_password'),
]
