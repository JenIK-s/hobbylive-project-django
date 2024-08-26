from django.db import models
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

User = get_user_model()


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

    def __str__(self):
        return self.name


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
    discount = models.IntegerField(
        default=0,
        verbose_name="Скидка в процентах"
    )
    price_not_discount = models.IntegerField(
        default=100,
        verbose_name="Цена"
    )
    description = models.TextField(
        verbose_name="Описание"
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    @property
    def price(self):
        return self.price_not_discount - (self.price_not_discount * (self.discount / 100))

    def __str__(self):
        return self.name


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

    def __str__(self):
        return f"{self.product.name} | {self.image}"


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

    def __str__(self):
        return f"{self.product.name} | {self.characteristic.name}"


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
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

    def __str__(self):
        return f"{self.user} Cart"


class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )
    image = models.ForeignKey(
        ProductImage,
        on_delete=models.CASCADE,
        verbose_name="Изображение",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"

    def __str__(self):
        return f"{self.user} Wishlist"


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
    image = models.ImageField(
        upload_to="categories_photo/",
        verbose_name="Изображение"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class ProductInOrder(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )
    image = models.ForeignKey(
        ProductImage,
        on_delete=models.CASCADE,
        verbose_name="Изображение",
    )
    count = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"

    def __str__(self):
        return f"{self.user.name} | {self.product.name} Cart"


class Order(models.Model):
    choises = (
        ("Собирается", "Собирается"),
        ("В пути", "В пути"),
        ("Доставлено", "Доставлено"),
        ("Получено", "Получено")
    )
    products = models.ManyToManyField(
        ProductInOrder,
        verbose_name="Продукт",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    status = models.CharField(
        max_length=255,
        default='Собирается',
        choices=choises,
        verbose_name='Статус доставки'
    )
    date = models.DateTimeField(auto_now=True)
    total_price = models.IntegerField()
    address = models.CharField(max_length=1000)
    carrier = models.CharField(
        max_length=255,
        verbose_name='Перевозчик'
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"{self.user.name} Order"
