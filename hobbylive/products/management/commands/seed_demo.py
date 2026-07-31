from pathlib import Path
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageEnhance, ImageOps

from products.models import (
    Cart,
    Categories,
    Characteristic,
    Order,
    ParameterValue,
    Product,
    ProductCharacteristic,
    ProductImage,
    ProductInOrder,
    ProductPopularity,
    UserInterest,
    Wishlist,
)


CATEGORY_TREE = [
    ("Электроника", ["Наушники", "Гаджеты", "Аудио", "Питание"]),
    ("Дом и быт", ["Освещение", "Хранение", "Кухня", "Текстиль"]),
    ("Спорт", ["Йога", "Силовые", "Аксессуары", "Фитнес"]),
    ("Одежда", ["Футболки", "Верхняя одежда", "Обувь", "Джинсы"]),
    ("Красота", ["Уход за лицом", "Уход за руками", "Наборы", "Волосы"]),
    ("Аксессуары", ["Рюкзаки", "Сумки", "Кошельки", "Очки"]),
]

ROOT_PHOTOS = {
    "Электроника": "c_electronics.jpg",
    "Дом и быт": "c_home.jpg",
    "Спорт": "c_sport.jpg",
    "Одежда": "c_clothes.jpg",
    "Красота": "c_beauty.jpg",
    "Аксессуары": "c_accessories.jpg",
}

SUB_PHOTOS = {
    "Наушники": "p_headphones.jpg",
    "Гаджеты": "p_watch.jpg",
    "Аудио": "p_speaker.jpg",
    "Питание": "p_powerbank.jpg",
    "Освещение": "p_lamp.jpg",
    "Хранение": "p_organizer.jpg",
    "Кухня": "p_cookware.jpg",
    "Текстиль": "p_blanket.jpg",
    "Йога": "p_yoga.jpg",
    "Силовые": "p_dumbbells.jpg",
    "Аксессуары": "p_bottle.jpg",
    "Фитнес": "p_bands.jpg",
    "Футболки": "p_tshirt.jpg",
    "Верхняя одежда": "p_hoodie.jpg",
    "Обувь": "p_sneakers.jpg",
    "Джинсы": "p_jeans.jpg",
    "Уход за лицом": "p_serum.jpg",
    "Уход за руками": "p_cream.jpg",
    "Наборы": "p_faceset.jpg",
    "Волосы": "p_hairspray.jpg",
    "Рюкзаки": "p_backpack.jpg",
    "Сумки": "p_bag.jpg",
    "Кошельки": "p_wallet.jpg",
    "Очки": "p_glasses.jpg",
}

# (name, root_index, sub_index, price, discount, description, colors, sizes, photo_file)
PRODUCTS = [
    ("Беспроводные наушники Pulse X", 0, 0, 4990, 15, "Лёгкие наушники с активным шумоподавлением и автономностью до 30 часов.", ["Чёрный", "Белый"], None, "p_headphones.jpg"),
    ("Смарт-часы Nova Watch", 0, 1, 8990, 10, "Умные часы с пульсометром, GPS и защитой от влаги IP68.", ["Графит", "Серебро"], ["40 мм", "44 мм"], "p_watch.jpg"),
    ("Портативная колонка Boom Mini", 0, 2, 3490, 0, "Компактная Bluetooth-колонка с насыщенным басом и защитой от брызг.", ["Чёрный", "Синий"], None, "p_speaker.jpg"),
    ("Powerbank 20000 mAh", 0, 3, 2790, 20, "Быстрая зарядка двух устройств одновременно. Компактный корпус.", ["Чёрный", "Белый"], None, "p_powerbank.jpg"),
    ("Настольная лампа Glow", 1, 0, 2190, 0, "Тёплый свет, регулировка яркости, USB-зарядка телефона на основании.", ["Белый", "Чёрный"], None, "p_lamp.jpg"),
    ("Органайзер для кухни", 1, 1, 1590, 5, "Металлический органайзер для столовых приборов и мелочей.", ["Хром", "Чёрный"], None, "p_organizer.jpg"),
    ("Набор посуды Everyday 6 пр.", 1, 2, 4590, 12, "Керамическое покрытие, подходит для индукции и посудомойки.", ["Серый", "Кремовый"], None, "p_cookware.jpg"),
    ("Плед Soft Home 150×200", 1, 3, 3290, 0, "Мягкий плед из микрофибры — для дивана и путешествий.", ["Бежевый", "Серый", "Зелёный"], None, "p_blanket.jpg"),
    ("Коврик для йоги ProMat", 2, 0, 2490, 0, "Нескользящий коврик толщиной 6 мм с чехлом в комплекте.", ["Синий", "Серый", "Розовый"], None, "p_yoga.jpg"),
    ("Гантели 2×5 кг", 2, 1, 3890, 8, "Пара гантелей с неопреновым покрытием для комфортных тренировок дома.", ["Чёрный", "Красный"], None, "p_dumbbells.jpg"),
    ("Спортивная бутылка 750 мл", 2, 2, 990, 0, "Герметичная бутылка из Tritan, не впитывает запахи.", ["Бирюзовый", "Чёрный", "Розовый"], None, "p_bottle.jpg"),
    ("Фитнес-резинки Set 5", 2, 3, 1490, 25, "Набор из пяти лент разной нагрузки + мешочек для хранения.", ["Микс"], None, "p_bands.jpg"),
    ("Футболка Daily Cotton", 3, 0, 1890, 0, "Базовая футболка из плотного хлопка, свободный крой.", ["Белый", "Чёрный", "Олива"], ["S", "M", "L", "XL"], "p_tshirt.jpg"),
    ("Худи Urban Soft", 3, 1, 4490, 15, "Утеплённое худи с капюшоном и карманом-кенгуру.", ["Серый", "Чёрный"], ["M", "L", "XL", "XXL"], "p_hoodie.jpg"),
    ("Кроссовки Runner Lite", 3, 2, 6990, 10, "Лёгкие кроссовки для города и лёгкого бега.", ["Белый", "Чёрный"], ["40", "41", "42", "43", "44"], "p_sneakers.jpg"),
    ("Джинсы Straight Fit", 3, 3, 5490, 0, "Классические джинсы средней посадки, плотный деним.", ["Синий", "Чёрный"], ["30", "32", "34", "36"], "p_jeans.jpg"),
    ("Сыворотка Hydra Boost", 4, 0, 2590, 0, "Увлажняющая сыворотка с гиалуроновой кислотой для ежедневного ухода.", ["Стандарт"], ["30 мл", "50 мл"], "p_serum.jpg"),
    ("Крем для рук Soft Care", 4, 1, 690, 0, "Лёгкий крем с пантенолом, быстро впитывается.", ["Классический", "Алоэ"], None, "p_cream.jpg"),
    ("Набор ухода Face Duo", 4, 2, 3990, 18, "Очищающий гель и увлажняющий крем в одном наборе.", ["Базовый", "Sensitive"], None, "p_faceset.jpg"),
    ("Спрей для волос Volume", 4, 3, 1290, 5, "Лёгкая фиксация и объём у корней без липкости.", ["Стандарт"], ["150 мл", "250 мл"], "p_hairspray.jpg"),
    ("Рюкзак City Daypack", 5, 0, 4290, 0, "Городской рюкзак 20 л с отделением для ноутбука 15\".", ["Чёрный", "Хаки"], None, "p_backpack.jpg"),
    ("Сумка через плечо Mini", 5, 1, 2790, 10, "Компактная сумка для документов и повседневных вещей.", ["Коричневый", "Чёрный"], None, "p_bag.jpg"),
    ("Кошелёк Slim Card", 5, 2, 1590, 0, "Тонкий кошелёк из экокожи на 8 карт.", ["Чёрный", "Коричневый"], None, "p_wallet.jpg"),
    ("Очки Daylight UV400", 5, 3, 2190, 12, "Солнцезащитные очки с защитой UV400 и лёгкой оправой.", ["Чёрный", "Коричневый"], None, "p_glasses.jpg"),
]

COLOR_TINTS = {
    "Чёрный": (0.92, 0.88, 0.85),
    "Белый": (1.08, 1.06, 1.1),
    "Синий": (0.9, 0.95, 1.15),
    "Серый": (0.98, 0.98, 0.98),
    "Красный": (1.15, 0.9, 0.9),
    "Розовый": (1.12, 0.95, 1.05),
    "Бирюзовый": (0.9, 1.05, 1.12),
    "Зелёный": (0.92, 1.1, 0.95),
    "Бежевый": (1.08, 1.04, 0.95),
    "Кремовый": (1.1, 1.06, 0.98),
    "Олива": (0.95, 1.05, 0.9),
    "Хаки": (1.0, 1.04, 0.9),
    "Коричневый": (1.08, 0.98, 0.88),
    "Графит": (0.94, 0.94, 0.96),
    "Серебро": (1.05, 1.05, 1.08),
    "Хром": (1.06, 1.06, 1.08),
    "Микс": (1.0, 1.0, 1.0),
    "Стандарт": (1.0, 1.0, 1.0),
    "Классический": (1.0, 1.0, 1.0),
    "Алоэ": (0.95, 1.08, 0.98),
    "Базовый": (1.0, 1.0, 1.0),
    "Sensitive": (1.05, 1.02, 1.06),
}


def demo_root():
    return Path(settings.BASE_DIR) / "static" / "demo_photos"


def fit_image(src: Path, dest: Path, size, tint=None):
    dest.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(src).convert("RGB")
    img = ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)
    if tint:
        r, g, b = img.split()
        r = r.point(lambda x: min(255, int(x * tint[0])))
        g = g.point(lambda x: min(255, int(x * tint[1])))
        b = b.point(lambda x: min(255, int(x * tint[2])))
        img = Image.merge("RGB", (r, g, b))
        img = ImageEnhance.Contrast(img).enhance(1.05)
    img.save(dest, format="JPEG", quality=88, optimize=True)


class Command(BaseCommand):
    help = "Пересоздаёт каталог с фото из static/demo_photos"

    @transaction.atomic
    def handle(self, *args, **options):
        media = Path(settings.MEDIA_ROOT)
        products_dir = media / "products_photo"
        categories_dir = media / "categories_photo"
        photos = demo_root()
        prod_src = photos / "products"
        cat_src = photos / "categories"

        if not prod_src.exists() or not cat_src.exists():
            raise SystemExit(
                f"Нет демо-фото в {photos}. Сначала положите jpg в products/ и categories/."
            )

        self.stdout.write("Очистка БД…")
        Order.objects.all().delete()
        ProductInOrder.objects.all().delete()
        Cart.objects.all().delete()
        Wishlist.objects.all().delete()
        ProductImage.objects.all().delete()
        ProductCharacteristic.objects.all().delete()
        ProductPopularity.objects.all().delete()
        UserInterest.objects.all().delete()
        Product.objects.all().delete()
        Categories.objects.all().delete()
        Characteristic.objects.all().delete()
        ParameterValue.objects.all().delete()

        self.stdout.write("Очистка media…")
        for folder in (products_dir, categories_dir):
            if folder.exists():
                shutil.rmtree(folder)
            folder.mkdir(parents=True, exist_ok=True)

        weight = Characteristic.objects.create(name="Вес", measurement_unit="г")
        size_char = Characteristic.objects.create(
            name="Размер упаковки", measurement_unit="см"
        )

        self.stdout.write("Категории…")
        roots_by_name = {}
        leaves = [[] for _ in CATEGORY_TREE]
        cat_img = 0

        for root_idx, (root_name, sub_names) in enumerate(CATEGORY_TREE):
            cat_img += 1
            rel = f"categories_photo/cat_{cat_img:02d}.jpg"
            fit_image(
                cat_src / ROOT_PHOTOS[root_name],
                media / rel,
                (1200, 900),
            )
            root = Categories(name=root_name, parent=None)
            root.image.name = rel
            root.save()
            roots_by_name[root_name] = root

            for sub_name in sub_names:
                cat_img += 1
                rel = f"categories_photo/cat_{cat_img:02d}.jpg"
                fit_image(
                    prod_src / SUB_PHOTOS[sub_name],
                    media / rel,
                    (1200, 900),
                )
                child = Categories(name=sub_name, parent=root)
                child.image.name = rel
                child.save()
                leaves[root_idx].append(child)

        self.stdout.write("Товары…")
        created = 0
        image_count = 0
        param_cache = {}

        for p_idx, row in enumerate(PRODUCTS, start=1):
            name, root_idx, sub_idx, price, discount, description, variants, sizes, photo = row
            product = Product.objects.create(
                name=name,
                discount=discount,
                price_not_discount=price,
                description=description,
                parameters=(
                    "Объём"
                    if sizes and any("мл" in s or "мм" in s for s in sizes)
                    else ("Размер" if sizes else "")
                ),
                measurement_unit="",
            )
            leaves[root_idx][sub_idx].product.add(product)

            if sizes:
                for size_label in sizes:
                    if size_label not in param_cache:
                        param_cache[size_label] = ParameterValue.objects.create(
                            value=size_label
                        )
                    product.parameters_value.add(param_cache[size_label])

            ProductCharacteristic.objects.create(
                product=product,
                characteristic=weight,
                amount=max(1, (price // 50) % 900 + 100),
            )
            ProductCharacteristic.objects.create(
                product=product,
                characteristic=size_char,
                amount=max(1, (price // 100) % 40 + 10),
            )

            colors = variants or ["Стандарт"]
            src = prod_src / photo
            for v_idx, color in enumerate(colors, start=1):
                rel = f"products_photo/p_{p_idx:02d}_{v_idx}.jpg"
                tint = COLOR_TINTS.get(color) if v_idx > 1 else None
                fit_image(src, media / rel, (900, 900), tint=tint)
                img = ProductImage(product=product, color=color)
                img.image.name = rel
                img.save()
                image_count += 1

            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: {len(roots_by_name)} разделов, "
                f"{sum(len(x) for x in leaves)} подкатегорий, "
                f"{created} товаров, {image_count} фото"
            )
        )
