from django.db import models
from common.models import BaseModel
from core.models import User
import uuid


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)

    contact_number = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return self.name


class UserAddress(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_address")
    is_default = models.BooleanField(null=True, blank=True, default=False)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    address_line_1 = models.TextField(blank=True, max_length=1500)
    address_line_2 = models.TextField(blank=True, max_length=1500)

    def __unicode__(self):
        return f'{self.user} - {self.postal_code}'
