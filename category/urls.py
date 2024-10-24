from django.urls import path
from . import views


urlpatterns = [
    path('setup/category/list', views.list_category, name='list_category'),
    path('setup/category/add', views.add_category, name='add_category'),
]
