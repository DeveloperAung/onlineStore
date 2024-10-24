from django.apps import AppConfig
from django.db.models.signals import post_migrate


class BrandConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'brand'

    def ready(self):
        post_migrate.connect(create_default_data, sender=self)


def create_default_data(sender, **kwargs):
    from brand.models import Brand
    if not Brand.objects.exists():  # Check if data already exists

        brands = [
            Brand(brand_name='အရီးတောင်း', slug='a_yee_taung',
                  description='စားကောင်းလျှင် အရီးတောင်း အရီးတောင်းဆို လက်ဖက်ကောင်း နှစ်ပေါင်း တရာကျော် လူကြိုက်များခဲ့တဲ့ မန္တလေး အရီးတောင်းလက်ဖက်က ထုတ်လုပ်တဲ့ အရီးတောင်း ဇယန်းနှပ်လေးဖြစ်ပါတယ်။',
                  brand_logo='photos/brand/TheNextLevel_logo.png'),
            Brand(brand_name='အင်းဝ', slug='inn_wa',
                  description='စားကြမယ် ချက်ကြမယ် Facebook Group ထဲမှ ဟင်းချက်နည်းများကိုမျှဝေပေးနေတဲ့ မြန်မာပြည်မှ နာမည်‌ကြီး မပန်းခရေကြီး ရဲ့ သဘာဝအတိုင်း',
                  brand_logo='photos/brand/gps.png')
        ]

        # Use bulk_create to insert all instances in one query
        Brand.objects.bulk_create(brands)
