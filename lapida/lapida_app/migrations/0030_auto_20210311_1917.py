# Generated by Django 3.1.5 on 2021-03-11 11:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lapida_app', '0029_masterdata_revised_order_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='masterdata_revised',
            old_name='order_date',
            new_name='birthdate',
        ),
    ]