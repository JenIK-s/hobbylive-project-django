# Generated by Django 4.2 on 2024-08-28 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0040_alter_product_parameters'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parametervalue',
            name='parameter',
        ),
        migrations.AddField(
            model_name='product',
            name='parameters_value',
            field=models.ManyToManyField(blank=True, related_name='products', to='products.parametervalue', verbose_name='Параметры'),
        ),
        migrations.RemoveField(
            model_name='product',
            name='parameters',
        ),
        migrations.DeleteModel(
            name='Parameter',
        ),
        migrations.AddField(
            model_name='product',
            name='parameters',
            field=models.CharField(default=True, max_length=100, verbose_name='Параметр'),
            preserve_default=False,
        ),
    ]
