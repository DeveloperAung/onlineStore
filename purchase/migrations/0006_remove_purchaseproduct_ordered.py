# Generated by Django 5.1.2 on 2024-10-25 06:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0005_alter_purchase_purchase_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseproduct',
            name='ordered',
        ),
    ]
