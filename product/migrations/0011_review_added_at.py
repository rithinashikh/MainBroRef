# Generated by Django 4.1.7 on 2023-05-02 03:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='added_at',
            field=models.DateTimeField(default=django.utils.timezone.localtime),
        ),
    ]
