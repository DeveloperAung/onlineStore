# Generated by Django 5.1.2 on 2024-10-25 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0004_alter_purchase_purchase_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='purchase_date',
            field=models.DateTimeField(),
        ),
    ]