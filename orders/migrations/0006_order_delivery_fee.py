# Generated by Django 5.1.2 on 2024-11-01 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_paymentmethod_delivery_amount_alter_order_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_fee',
            field=models.FloatField(default=0),
        ),
    ]
