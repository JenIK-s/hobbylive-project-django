# Generated by Django 4.2 on 2024-08-26 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0028_order_carrier_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='categories',
            name='image',
            field=models.ImageField(default=True, upload_to='categories_photo/', verbose_name='Изображение'),
            preserve_default=False,
        ),
    ]
