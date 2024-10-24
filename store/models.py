from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse

from brand.models import Brand
from category.models import Category
from common.models import BaseModel
from common.utlis import compress_image


class Product(BaseModel):
    code = models.CharField(max_length=15, unique=True)
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=2500, blank=True)
    price = models.FloatField(default=0)
    images = models.ImageField(blank=True, null=True, upload_to='photos/products', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
    ])
    low_lvl_stock = models.FloatField(default=1)
    is_use_low_stock = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)

    def get_url(self):
        return reverse('details_product', args=[self.category.slug, self.slug])

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
