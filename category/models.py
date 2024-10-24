from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from common.models import BaseModel
from common.utlis import compress_image


class Category(BaseModel):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=2500, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True, null=True, validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
    ])

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def save(self, *args, **kwargs):
        if self.cat_image and hasattr(self.cat_image, 'file'):
            img, img_io = compress_image(self.cat_image)
            self.cat_image.save(self.cat_image.name, ContentFile(img_io.getvalue()), save=False)
            super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.category_name
