# Generated by Django 3.1.5 on 2021-03-07 03:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lapida_app', '0023_order_user_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order_user',
            name='image',
        ),
    ]