# Generated by Django 4.1.7 on 2023-04-11 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0016_order_canceled_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='returned_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('processed', 'processed'), ('out for shipping', 'out for shipping'), ('canceled', 'canceled'), ('shipped', 'shipped'), ('out for delivery', 'out for delivery'), ('delivered', 'delivered'), ('return', 'return'), ('refunded', 'refunded')], default='pending', max_length=200),
        ),
    ]
