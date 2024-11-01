import random

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from core.middleware import CurrentUserMiddleware


class BaseModel(models.Model):
    description = models.TextField(max_length=3500, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   related_name='%(class)s_created', null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    related_name='%(class)s_modified', null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   related_name='%(class)s_deleted', null=True, blank=True)
    deleted_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True  # Make this model abstract, so it won't create a database table for it

    def __str__(self):
        return f"{self.pk} - {self.__class__.__name__}"

    def save(self, *args, **kwargs):
        current_user = CurrentUserMiddleware.get_current_user()  # Get the current user from the middleware

        if not self.pk and current_user:
            self.created_by = current_user if current_user.is_authenticated else None
            self.modified_by = current_user if current_user.is_authenticated else None

        if current_user:
            self.modified_by = current_user if current_user.is_authenticated else None

        super(BaseModel, self).save(*args, **kwargs)


class Status(BaseModel):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    parent_code = models.CharField(max_length=10, blank=True, null=True)
    status_code = models.CharField(max_length=10, unique=True)
    internal_status = models.CharField(max_length=255, blank=True)
    external_status = models.CharField(max_length=255, blank=True)
    description = models.TextField(max_length=350, blank=True, null=True)

    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Status'

        unique_together = ('internal_status', 'parent_code')

    def save(self, *args, **kwargs):
        self.parent_code = self.parent.status_code if self.parent else None
        if not self.external_status:
            self.external_status = self.internal_status
        super().save(*args, **kwargs)

    def __str__(self):
        status = self.parent.internal_status if self.parent else ''
        return f'{status} - {self.internal_status}'


# Define a regex pattern that allows only English characters and numbers
alphanumeric_validator = RegexValidator(r'^[a-zA-Z0-9]*$', 'Only English letters and numbers are allowed.')


def generate_unique_number(model_obj):
    # Generate a random 8-digit number and ensure uniqueness
    while True:
        number = str(random.randint(10000000, 99999999))  # Generate an 8-digit number
        if not model_obj.objects.filter(slug=number).exists():
            return number


def validate_file_size(value):
    file_size = value.size
    max_size = 300 * 1024 * 1024  # 300MB in bytes

    if file_size > max_size:
        raise ValidationError(f"The maximum file size that can be uploaded is 300MB.")
    return value
