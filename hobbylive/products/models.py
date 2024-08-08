from django.db import models
from django.contrib.sessions.models import Session


class Characteristic(models.Model):
    name = models.CharField(
        max_length=500,
        verbose_name="Наименование",
    )
    measurement_unit = models.CharField(
        max_length=100,
        verbose_name="Единицы измерения",
    )

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"


class Product(models.Model):
    name = models.CharField(
        max_length=500,
        verbose_name="Наименование",
    )
    characteristics = models.ManyToManyField(
        Characteristic,
        through="ProductCharacteristic",
        verbose_name="Характеристики"
    )
    price = models.IntegerField(
        default=100,
        verbose_name="Цена"
    )
    description = models.TextField(
        verbose_name="Описание"
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class ProductImage(models.Model):
    image = models.ImageField(
        upload_to="products_photo/",
        verbose_name="Изображение"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Продукт"
    )

    class Meta:
        verbose_name = "Изображения продукта"
        verbose_name_plural = "Изображения продуктов"


class ProductCharacteristic(models.Model):
    characteristic = models.ForeignKey(
        Characteristic,
        on_delete=models.CASCADE,
        verbose_name="Характеристика"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="characteristic",
        verbose_name="Продукт"
    )

    class Meta:
        verbose_name = "Характеристика продукта"
        verbose_name_plural = "Характеристики продуктов"


class Cart(models.Model):
    # session = models.ForeignKey(
    #     Session,
    #     on_delete=models.CASCADE,
    #     verbose_name="Сессия"
    # )
    session = models.CharField(
        max_length=255,
        verbose_name="Сессия"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Продукт",
        related_name="product"
    )
    image = models.ForeignKey(
        ProductImage,
        on_delete=models.CASCADE,
        verbose_name="Изображение",
        related_name="image_product"
    )
    count = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class Wishlist(models.Model):
    pass

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"


class Categories(models.Model):
    name = models.CharField(
        max_length=500,
        verbose_name="Наименование",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="Categories",
        verbose_name="Продукт"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"




