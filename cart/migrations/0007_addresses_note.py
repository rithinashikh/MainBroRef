# Generated by Django 4.1.7 on 2023-04-01 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_addresstype_remove_shippingaddress_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='addresses',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
