from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ParameterValue(models.Model):
    value = models.CharField(
        max_length=100,
        verbose_name="Значение параметра"
    )

    class Meta:
        verbose_name = "Значение параметра"
        verbose_name_plural = "Значения параметра"

    def __str__(self):
        return self.value


class Characteristic(models.Model):
    name = models.CharField(
        max_length=500,
        verbose_name="Наименование",
    )
    measurement_unit = models.CharField(
        max_length=100,
        verbose_name="Единицы измерения",
        blank=True,
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
    parameters = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Параметр",
    )
    parameters_value = models.ManyToManyField(
        ParameterValue,
        blank=True,
        related_name="products",
        verbose_name="Параметры"
    )
    measurement_unit = models.CharField(
        max_length=100,
        verbose_name="Единицы измерения",
        blank=True,
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    @property
    def price(self):
        return int(
            self.price_not_discount
            - (self.price_not_discount * (self.discount / 100))
        )

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    image = models.ImageField(
        upload_to="products_photo/",
        verbose_name="Изображение"
    )
    color = models.CharField(
        max_length=100,
        verbose_name="Цвет",
        blank=True,
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
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, 'Количество не может быть меньше 1'
            )
        ],
        verbose_name='Количество',
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
    count = models.IntegerField(
        default=1,
        blank=True
    )
    parameters = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Параметр",
    )
    parameters_value = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Значение параметра",
    )
    measurement_unit = models.CharField(
        max_length=100,
        verbose_name="Единицы измерения",
        blank=True,
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name="Родительская категория",
    )
    product = models.ManyToManyField(
        Product,
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
        if self.parent_id:
            return f"{self.parent.name} → {self.name}"
        return self.name

    @property
    def is_root(self):
        return self.parent_id is None

    def has_children(self):
        return self.children.exists()


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
    parameters = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Параметр",
    )
    parameters_value = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Значение параметра",
    )
    measurement_unit = models.CharField(
        max_length=100,
        verbose_name="Единицы измерения",
        blank=True,
    )

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"

    def __str__(self):
        return f"{self.user.username} | {self.product.name}"


class Order(models.Model):
    STATUS_CREATED = "Создан"
    STATUS_ASSEMBLY = "Собирается"
    STATUS_SHIPPING = "В пути"
    STATUS_DELIVERED = "Доставлено"
    STATUS_RECEIVED = "Получено"
    STATUS_CANCELLED = "Отменен"

    FLOW = (
        STATUS_CREATED,
        STATUS_ASSEMBLY,
        STATUS_SHIPPING,
        STATUS_DELIVERED,
        STATUS_RECEIVED,
    )

    # Следующее действие для суперпользователя: текущий статус → (новый статус, текст кнопки)
    STATUS_ACTIONS = {
        STATUS_CREATED: (STATUS_ASSEMBLY, "Товар собирается"),
        STATUS_ASSEMBLY: (STATUS_SHIPPING, "Передали в доставку"),
        STATUS_SHIPPING: (STATUS_DELIVERED, "Товар доставлен"),
        STATUS_DELIVERED: (STATUS_RECEIVED, "Клиент получил заказ"),
    }

    choises = (
        (STATUS_CREATED, STATUS_CREATED),
        (STATUS_ASSEMBLY, STATUS_ASSEMBLY),
        (STATUS_SHIPPING, STATUS_SHIPPING),
        (STATUS_DELIVERED, STATUS_DELIVERED),
        (STATUS_RECEIVED, STATUS_RECEIVED),
        (STATUS_CANCELLED, STATUS_CANCELLED),
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
        default='Создан',
        choices=choises,
        verbose_name='Статус доставки'
    )
    date = models.DateTimeField(auto_now_add=True)
    total_price = models.IntegerField(
        verbose_name="Сумма к оплате"
    )
    address = models.CharField(
        max_length=1000,
        verbose_name="Адрес"
    )
    carrier = models.CharField(
        max_length=255,
        verbose_name='Перевозчик'
    )
    first_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Фамилия",
    )
    phone = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name="Телефон",
    )
    comment = models.CharField(
        max_length=1000,
        blank=True,
        default="",
        verbose_name="Комментарий",
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"{self.user.username} Order"

    def status_track(self):
        """Шаги дорожки статуса для шаблона."""
        if self.status == self.STATUS_CANCELLED:
            return {
                "cancelled": True,
                "steps": [
                    {"label": label, "state": "muted"} for label in self.FLOW
                ],
            }

        try:
            current_idx = self.FLOW.index(self.status)
        except ValueError:
            current_idx = 0

        steps = []
        for idx, label in enumerate(self.FLOW):
            if idx < current_idx:
                state = "done"
            elif idx == current_idx:
                state = "current"
            else:
                state = "todo"
            steps.append({"label": label, "state": state})
        return {"cancelled": False, "steps": steps}

    def next_status_action(self):
        """Кнопка следующего шага для суперпользователя, либо None."""
        action = self.STATUS_ACTIONS.get(self.status)
        if not action:
            return None
        next_status, label = action
        return {"status": next_status, "label": label}


class ProductPopularity(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="popularity",
        verbose_name="Товар",
    )
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    search_hits = models.PositiveIntegerField(default=0, verbose_name="Попадания в поиск")
    wishlist_adds = models.PositiveIntegerField(default=0, verbose_name="В избранное")
    cart_adds = models.PositiveIntegerField(default=0, verbose_name="В корзину")
    purchases = models.PositiveIntegerField(default=0, verbose_name="Покупки")
    score = models.PositiveIntegerField(default=0, db_index=True, verbose_name="Рейтинг")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Популярность товара"
        verbose_name_plural = "Популярность товаров"
        ordering = ["-score"]

    def recalculate_score(self):
        self.score = (
            self.views * 1
            + self.search_hits * 2
            + self.wishlist_adds * 3
            + self.cart_adds * 5
            + self.purchases * 10
        )
        return self.score

    def __str__(self):
        return f"{self.product.name} · {self.score}"


class UserInterest(models.Model):
    KIND_PRODUCT = "product"
    KIND_CATEGORY = "category"
    KIND_QUERY = "query"
    KIND_CHOICES = (
        (KIND_PRODUCT, "Товар"),
        (KIND_CATEGORY, "Категория"),
        (KIND_QUERY, "Поиск"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="interests",
        verbose_name="Пользователь",
    )
    kind = models.CharField(
        max_length=20,
        choices=KIND_CHOICES,
        verbose_name="Тип",
    )
    key = models.CharField(
        max_length=255,
        verbose_name="Ключ",
    )
    weight = models.FloatField(default=0, verbose_name="Вес")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Интерес пользователя"
        verbose_name_plural = "Интересы пользователей"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "kind", "key"],
                name="uniq_user_interest_kind_key",
            )
        ]
        indexes = [
            models.Index(fields=["user", "kind", "-weight"]),
        ]

    def __str__(self):
        return f"{self.user_id} · {self.kind}:{self.key} = {self.weight}"
