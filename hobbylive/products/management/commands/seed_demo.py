from pathlib import Path
import hashlib
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont

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
    Wishlist,
)


# Корневая категория → список подкатегорий
CATEGORY_TREE = [
    ("Электроника", ["Наушники", "Гаджеты", "Аудио", "Питание"]),
    ("Дом и быт", ["Освещение", "Хранение", "Кухня", "Текстиль"]),
    ("Спорт", ["Йога", "Силовые", "Аксессуары", "Фитнес"]),
    ("Одежда", ["Футболки", "Верхняя одежда", "Обувь", "Джинсы"]),
    ("Красота", ["Уход за лицом", "Уход за руками", "Наборы", "Волосы"]),
    ("Аксессуары", ["Рюкзаки", "Сумки", "Кошельки", "Очки"]),
]

# (name, root_index, sub_index, price, discount, description, colors, sizes)
PRODUCTS = [
    ("Беспроводные наушники Pulse X", 0, 0, 4990, 15, "Лёгкие наушники с активным шумоподавлением и автономностью до 30 часов.", ["Чёрный", "Белый"], None),
    ("Смарт-часы Nova Watch", 0, 1, 8990, 10, "Умные часы с пульсометром, GPS и защитой от влаги IP68.", ["Графит", "Серебро"], ["40 мм", "44 мм"]),
    ("Портативная колонка Boom Mini", 0, 2, 3490, 0, "Компактная Bluetooth-колонка с насыщенным басом и защитой от брызг.", ["Чёрный", "Синий"], None),
    ("Powerbank 20000 mAh", 0, 3, 2790, 20, "Быстрая зарядка двух устройств одновременно. Компактный корпус.", ["Чёрный", "Белый"], None),
    ("Настольная лампа Glow", 1, 0, 2190, 0, "Тёплый свет, регулировка яркости, USB-зарядка телефона на основании.", ["Белый", "Чёрный"], None),
    ("Органайзер для кухни", 1, 1, 1590, 5, "Металлический органайзер для столовых приборов и мелочей.", ["Хром", "Чёрный"], None),
    ("Набор посуды Everyday 6 пр.", 1, 2, 4590, 12, "Керамическое покрытие, подходит для индукции и посудомойки.", ["Серый", "Кремовый"], None),
    ("Плед Soft Home 150×200", 1, 3, 3290, 0, "Мягкий плед из микрофибры — для дивана и путешествий.", ["Бежевый", "Серый", "Зелёный"], None),
    ("Коврик для йоги ProMat", 2, 0, 2490, 0, "Нескользящий коврик толщиной 6 мм с чехлом в комплекте.", ["Синий", "Серый", "Розовый"], None),
    ("Гантели 2×5 кг", 2, 1, 3890, 8, "Пара гантелей с неопреновым покрытием для комфортных тренировок дома.", ["Чёрный", "Красный"], None),
    ("Спортивная бутылка 750 мл", 2, 2, 990, 0, "Герметичная бутылка из Tritan, не впитывает запахи.", ["Бирюзовый", "Чёрный", "Розовый"], None),
    ("Фитнес-резинки Set 5", 2, 3, 1490, 25, "Набор из пяти лент разной нагрузки + мешочек для хранения.", ["Микс"], None),
    ("Футболка Daily Cotton", 3, 0, 1890, 0, "Базовая футболка из плотного хлопка, свободный крой.", ["Белый", "Чёрный", "Олива"], ["S", "M", "L", "XL"]),
    ("Худи Urban Soft", 3, 1, 4490, 15, "Утеплённое худи с капюшоном и карманом-кенгуру.", ["Серый", "Чёрный"], ["M", "L", "XL", "XXL"]),
    ("Кроссовки Runner Lite", 3, 2, 6990, 10, "Лёгкие кроссовки для города и лёгкого бега.", ["Белый", "Чёрный"], ["40", "41", "42", "43", "44"]),
    ("Джинсы Straight Fit", 3, 3, 5490, 0, "Классические джинсы средней посадки, плотный деним.", ["Синий", "Чёрный"], ["30", "32", "34", "36"]),
    ("Сыворотка Hydra Boost", 4, 0, 2590, 0, "Увлажняющая сыворотка с гиалуроновой кислотой для ежедневного ухода.", ["Стандарт"], ["30 мл", "50 мл"]),
    ("Крем для рук Soft Care", 4, 1, 690, 0, "Лёгкий крем с пантенолом, быстро впитывается.", ["Классический", "Алоэ"], None),
    ("Набор ухода Face Duo", 4, 2, 3990, 18, "Очищающий гель и увлажняющий крем в одном наборе.", ["Базовый", "Sensitive"], None),
    ("Спрей для волос Volume", 4, 3, 1290, 5, "Лёгкая фиксация и объём у корней без липкости.", ["Стандарт"], ["150 мл", "250 мл"]),
    ("Рюкзак City Daypack", 5, 0, 4290, 0, "Городской рюкзак 20 л с отделением для ноутбука 15\".", ["Чёрный", "Хаки"], None),
    ("Сумка через плечо Mini", 5, 1, 2790, 10, "Компактная сумка для документов и повседневных вещей.", ["Коричневый", "Чёрный"], None),
    ("Кошелёк Slim Card", 5, 2, 1590, 0, "Тонкий кошелёк из экокожи на 8 карт.", ["Чёрный", "Коричневый"], None),
    ("Очки Daylight UV400", 5, 3, 2190, 12, "Солнцезащитные очки с защитой UV400 и лёгкой оправой.", ["Чёрный", "Коричневый"], None),
]

PALETTE = [
    ((15, 118, 110), (15, 20, 25)),
    ((30, 64, 175), (15, 23, 42)),
    ((180, 83, 9), (41, 37, 36)),
    ((126, 34, 206), (24, 24, 27)),
    ((185, 28, 28), (28, 25, 23)),
    ((4, 120, 87), (6, 78, 59)),
    ((67, 56, 202), (30, 27, 75)),
    ((14, 116, 144), (8, 47, 73)),
]


def _hash_color(text):
    digest = hashlib.md5(text.encode("utf-8")).hexdigest()
    return PALETTE[int(digest[:2], 16) % len(PALETTE)]


def _font(size):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _wrap(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:4]


def make_image(path, title, subtitle="", size=(900, 900), category=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    w, h = size
    top, bottom = _hash_color(title + subtitle)
    base = Image.new("RGB", (w, h), bottom)
    draw = ImageDraw.Draw(base)

    for y in range(h):
        t = y / max(h - 1, 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        draw.line([(0, y), (w, y)], fill=color)

    img = base.convert("RGBA")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    accent = tuple(min(255, c + 45) for c in top)
    od.ellipse([int(w * 0.42), int(-h * 0.15), int(w * 1.1), int(h * 0.5)], fill=(*accent, 75))
    od.ellipse([int(-w * 0.2), int(h * 0.55), int(w * 0.45), int(h * 1.2)], fill=(255, 255, 255, 28))
    od.rectangle([0, int(h * 0.58), w, h], fill=(15, 20, 25, 145 if not category else 120))
    img = Image.alpha_composite(img, overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    title_font = _font(54 if category else 42)
    sub_font = _font(28)
    badge_font = _font(22)

    lines = _wrap(draw, title, title_font, w - 100)
    y = int(h * 0.66)
    for line in lines:
        draw.text((48, y), line, font=title_font, fill=(255, 255, 255))
        y += int(getattr(title_font, "size", 42) * 1.2)

    if subtitle:
        draw.text((48, y + 8), subtitle, font=sub_font, fill=(220, 230, 230))

    badge = "DEMO" if not category else "КАТАЛОГ"
    bw = draw.textlength(badge, font=badge_font) + 28
    draw.rounded_rectangle([48, 48, 48 + bw, 92], radius=18, fill=(255, 255, 255))
    draw.text((62, 58), badge, font=badge_font, fill=bottom)

    img.save(path, quality=90, optimize=True)
    return path


class Command(BaseCommand):
    help = "Удаляет старый каталог/фото и генерирует тестовые карточки с новыми картинками"

    @transaction.atomic
    def handle(self, *args, **options):
        media = Path(settings.MEDIA_ROOT)
        products_dir = media / "products_photo"
        categories_dir = media / "categories_photo"

        self.stdout.write("Очистка БД…")
        Order.objects.all().delete()
        ProductInOrder.objects.all().delete()
        Cart.objects.all().delete()
        Wishlist.objects.all().delete()
        ProductImage.objects.all().delete()
        ProductCharacteristic.objects.all().delete()
        Product.objects.all().delete()
        Categories.objects.all().delete()
        Characteristic.objects.all().delete()
        ParameterValue.objects.all().delete()

        self.stdout.write("Очистка старых картинок…")
        for folder in (products_dir, categories_dir):
            if folder.exists():
                shutil.rmtree(folder)
            folder.mkdir(parents=True, exist_ok=True)

        weight = Characteristic.objects.create(name="Вес", measurement_unit="г")
        size_char = Characteristic.objects.create(name="Размер упаковки", measurement_unit="см")

        self.stdout.write("Генерация категорий…")
        roots = []
        leaves = []  # leaves[root_idx][sub_idx]
        cat_img = 0
        for root_idx, (root_name, sub_names) in enumerate(CATEGORY_TREE):
            cat_img += 1
            rel = f"categories_photo/cat_{cat_img:02d}.jpg"
            make_image(media / rel, root_name, subtitle="Раздел каталога", size=(1200, 900), category=True)
            root = Categories(name=root_name, parent=None)
            root.image.name = rel
            root.save()
            roots.append(root)

            row = []
            for sub_name in sub_names:
                cat_img += 1
                rel = f"categories_photo/cat_{cat_img:02d}.jpg"
                make_image(
                    media / rel,
                    sub_name,
                    subtitle=root_name,
                    size=(1200, 900),
                    category=True,
                )
                child = Categories(name=sub_name, parent=root)
                child.image.name = rel
                child.save()
                row.append(child)
            leaves.append(row)

        self.stdout.write("Генерация товаров и фото…")
        created = 0
        image_count = 0
        param_cache = {}

        for p_idx, (name, root_idx, sub_idx, price, discount, description, variants, sizes) in enumerate(PRODUCTS, start=1):
            product = Product.objects.create(
                name=name,
                discount=discount,
                price_not_discount=price,
                description=description,
                parameters="Объём" if sizes and any("мл" in s or "мм" in s for s in sizes) else ("Размер" if sizes else ""),
                measurement_unit="",
            )
            leaves[root_idx][sub_idx].product.add(product)

            if sizes:
                for size_label in sizes:
                    if size_label not in param_cache:
                        param_cache[size_label] = ParameterValue.objects.create(value=size_label)
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
            for v_idx, color in enumerate(colors, start=1):
                rel = f"products_photo/p_{p_idx:02d}_{v_idx}.jpg"
                make_image(
                    media / rel,
                    name,
                    subtitle=color or f"{product.price} ₽",
                    size=(900, 900),
                )
                img = ProductImage(product=product, color=color)
                img.image.name = rel
                img.save()
                image_count += 1

            created += 1

        total_cats = len(roots) + sum(len(row) for row in leaves)
        self.stdout.write(self.style.SUCCESS(
            f"Готово: {len(roots)} разделов, {total_cats - len(roots)} подкатегорий, "
            f"{created} товаров, {image_count} новых фото"
        ))
