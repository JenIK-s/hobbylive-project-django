# Generated by Django 4.2 on 2024-08-15 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.CharField(default=True, max_length=1000),
            preserve_default=False,
        ),
    ]
