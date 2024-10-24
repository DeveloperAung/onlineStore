from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CategoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'category'

    def ready(self):
        post_migrate.connect(create_default_data, sender=self)


def create_default_data(sender, **kwargs):
    from category.models import Category
    if not Category.objects.exists():  # Check if data already exists

        categories = [
            Category(category_name='လက်ဖက်', slug='tea-leaves-assorted-beans',
                  description='မြင်းခြံမြို့က နာမည်ကျော် ကံပွင့် လာပါပြီ။ ကံတွေပွင့်သွားအောင် ကြွပ်ရွနေတဲ့ ကံပွင့်ပဲစုံနှစ်ပြန်ကြော် လေးတွေ စားကြစို့။ ပါဝင်ပစ္စည်းများ။ ပဲကြီးအပွကြော်၊ ကုလားပဲခြမ်းကြော်၊ မြေပဲနီကြော်၊ ပဲလိပ်ပြာကြော်၊ နှမ်းလှော်၊ တောင်ကြီးပဲကြော်။',
                  cat_image='photos/categories/IMG_7967.jpeg'),
            Category(category_name='ရှမ်းခေါက်ဆွဲ', slug='shan_noodles',
                  description='Shan noodles are now a favorite in the Land of Golden Pagodas, although it is more common in the Mandalay region as well as the Shan state, where it originated. Shan is the easternmost state of Myanmar. It borders China, Thailand and Laos, which explains why variants of the Shan noodles recipe are popular in the Chinese Yunnan province as well as Chiang Mai in Thailand.',
                  cat_image='photos/categories/ni_im.jpg')
        ]

        # Use bulk_create to insert all instances in one query
        Category.objects.bulk_create(categories)
