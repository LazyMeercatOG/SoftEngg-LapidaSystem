# Generated by Django 3.1.5 on 2021-03-02 10:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lapida_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('category', models.CharField(choices=[('C', 'Cemetery'), ('CO', 'Columbarium')], max_length=2)),
                ('blk', models.CharField(max_length=3)),
                ('street', models.CharField(max_length=12)),
                ('lot', models.CharField(max_length=3)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
