# Generated by Django 4.1.7 on 2023-04-11 10:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0018_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_ordered',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
