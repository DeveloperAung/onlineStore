from .models import Brand


def menu_links(request):
    links = Brand.objects.filter(is_active=True)
    return dict(brand_links=links)
