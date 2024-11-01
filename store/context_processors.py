from .models import StoreInfo


def store_info(request):
    info = StoreInfo.objects.filter(is_active=True).last()
    return dict(info=info)
