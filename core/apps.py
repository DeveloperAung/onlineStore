from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        post_migrate.connect(create_default_data, sender=self)


def create_default_data(sender, **kwargs):
    from core.models import User
    if not User.objects.exists():  # Check if data already exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(username="admin", email="email@admin.com", password="123", user_type=1)
