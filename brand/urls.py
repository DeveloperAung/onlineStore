from django.urls import path
from . import views


urlpatterns = [
    path('setup/list', views.list_brand, name='list_brand'),
    path('setup/add', views.add_brand, name='add_brand'),
]
