from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from onlineStore import settings
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('account/', include('core.urls')),
    path('store/', include('store.urls')),
    path('category/', include('category.urls')),
    path('brand/', include('brand.urls')),
    path('cart/', include('carts.urls')),

    path('orders/', include('orders.urls')),
    path('purchase/', include('purchase.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

