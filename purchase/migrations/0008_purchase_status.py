# Generated by Django 5.1.2 on 2024-10-29 14:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_alter_status_parent_code'),
        ('purchase', '0007_alter_purchase_order_total_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='common.status'),
        ),
    ]
