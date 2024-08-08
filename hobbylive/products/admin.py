from django.contrib import admin
from .models import (
    Product, ProductImage, ProductCharacteristic,
    Cart, Categories, Wishlist,
    Characteristic
)


class ProductImageInline(admin.TabularInline):
    fk_name = "product"
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (ProductImageInline,)
    list_display = (
        "pk",
        "name",
        "price"
    )
    list_filter = ("name",)


@admin.register(ProductCharacteristic)
class ProductCharacteristicAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "product",
        "characteristic"
    )
    list_filter = ("product",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
    )
    list_filter = ("name",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    pass


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
    )
    list_filter = ("name",)
