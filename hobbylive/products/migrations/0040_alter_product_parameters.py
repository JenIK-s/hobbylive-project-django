# Generated by Django 4.2 on 2024-08-28 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0039_alter_parametervalue_parameter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='parameters',
            field=models.ManyToManyField(blank=True, related_name='products', to='products.parametervalue', verbose_name='Параметры'),
        ),
    ]
