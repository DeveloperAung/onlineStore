from PIL import Image, ImageOps
from io import BytesIO

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def compress_image(image):
    img = Image.open(image)

    # Convert image to RGB if it's RGBA
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    img = ImageOps.fit(img, (150, 143), Image.LANCZOS)

    img_io = BytesIO()
    img.save(img_io, format='JPEG', quality=90)
    return img, img_io


# This section is for all the common functions
def return_page_objs(request, pass_obj):
    paginator = Paginator(pass_obj, 1)  # 30 row per page
    page = request.GET.get('page', 1)

    try:
        page_objs = paginator.page(page)
        page_objs.adjusted_elided_pages = paginator.get_elided_page_range(page)
    except PageNotAnInteger:
        page_objs = paginator.page(1)
    except EmptyPage:
        page_objs = paginator.page(paginator.num_pages)

    # Create a query string with the current search parameters
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()
    return page_objs, query_string
