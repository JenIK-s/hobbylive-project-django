# Generated by Django 4.2 on 2024-06-21 23:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_categories_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='product',
            field=models.ForeignKey(default=True, on_delete=django.db.models.deletion.CASCADE, to='products.product', verbose_name='Продукт'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cart',
            name='session',
            field=models.CharField(default=True, max_length=255, verbose_name='Сессия'),
            preserve_default=False,
        ),
    ]
