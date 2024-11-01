from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse

from brand.models import Brand
from category.models import Category
from common.models import BaseModel
from common.utlis import compress_image


class StoreInfo(BaseModel):
    name = models.CharField(max_length=250)
    address = models.TextField(max_length=2500)
    email = models.EmailField(blank=True, null=True)
    contact = models.CharField(max_length=250)
    favico = models.ImageField(upload_to='photos/store/favico')
    logo = models.ImageField(upload_to='photos/store/logo')
    banner = models.ImageField(upload_to='photos/store/banner')

    def __str__(self):
        return self.name


class Unit(BaseModel):
    unit_code = models.CharField(max_length=5)
    unit_name = models.CharField(max_length=100)

    def __str__(self):
        return self.unit_name


class Product(BaseModel):
    code = models.CharField(max_length=15, unique=True)
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=2500, blank=True)
    price = models.FloatField(default=0)
    images = models.ImageField(blank=True, null=True, upload_to='photos/products', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
    ])
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    weight = models.FloatField(default=0)
    unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING, blank=True, null=True)
    low_lvl_stock = models.FloatField(default=1)
    is_use_low_stock = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)

    def get_url(self):
        return reverse('details_product', args=[self.category.slug, self.slug])

    def get_qty(self):
        from django.db.models import Sum
        total_qty = self.purchase_products.filter(is_active=True, product=self, available_qty__gt=0).aggregate(
            available_qty=Sum('available_qty'), balance_qty=Sum('balance_qty')
        )
        return {
            'available_qty': total_qty['available_qty'] or 0,
            'balance_qty': total_qty['balance_qty'] or 0
        }

    # def save(self, *args, **kwargs):
    #     if self.images and hasattr(self.images, 'file'):
    #         img, img_io = compress_image(self.images)
    #         self.images.save(self.images.name, ContentFile(img_io.getvalue()), save=False)
    #         super(Product, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.product_name


class ProductGallery(BaseModel):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'product gallery'
        verbose_name_plural = 'product gallery'
