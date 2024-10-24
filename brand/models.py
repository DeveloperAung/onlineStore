from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse

from common.models import BaseModel
from common.utlis import compress_image


class Brand(BaseModel):
    brand_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=2500, blank=True)
    brand_logo = models.ImageField(upload_to='photos/brand', blank=True, null=True, validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
    ])

    def get_url(self):
        return reverse('products_by_brand', args=[self.slug])

    def save(self, *args, **kwargs):
        if self.brand_logo and hasattr(self.brand_logo, 'file'):
            img, img_io = compress_image(self.brand_logo)
            self.brand_logo.save(self.brand_logo.name, ContentFile(img_io.getvalue()), save=False)
            super(Brand, self).save(*args, **kwargs)

    def __str__(self):
        return self.brand_name
