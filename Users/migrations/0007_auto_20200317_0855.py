# Generated by Django 3.0.2 on 2020-03-17 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0006_auto_20200317_0847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, default='images.png', upload_to='user_images/', verbose_name=''),
        ),
    ]
