# Generated by Django 4.2 on 2024-08-25 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0027_rename_price_product_price_not_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='carrier',
            field=models.CharField(default=True, max_length=255, verbose_name='Перевозчик'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Собирается', 'Собирается'), ('В пути', 'В пути'), ('Доставлено', 'Доставлено'), ('Получено', 'Получено')], default='Собирается', max_length=255, verbose_name='Статус доставки'),
        ),
    ]
