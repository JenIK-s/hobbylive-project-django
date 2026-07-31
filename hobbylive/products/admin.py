from django.contrib import admin
from .models import (
    Product, ProductImage, ProductCharacteristic,
    Cart, Categories, Wishlist,
    Characteristic, Order, ProductInOrder,
    ParameterValue, ProductPopularity, UserInterest,
)


@admin.register(ParameterValue)
class ParameterValueAdmin(admin.ModelAdmin):
    list_display = ("value",)


class ProductImageInline(admin.TabularInline):
    fk_name = "product"
    model = ProductImage


class ProductCharacteristicInline(admin.TabularInline):
    fk_name = "product"
    model = ProductCharacteristic


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (ProductImageInline, ProductCharacteristicInline)
    list_display = (
        "pk",
        "name",
        "price"
    )
    list_filter = ("name",)
    filter_horizontal = ("parameters_value",)


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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user"
    )


@admin.register(ProductInOrder)
class ProductInOrderAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "product"
    )


@admin.register(ProductPopularity)
class ProductPopularityAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "score",
        "views",
        "search_hits",
        "wishlist_adds",
        "cart_adds",
        "purchases",
        "updated_at",
    )
    list_filter = ("updated_at",)
    search_fields = ("product__name",)
    ordering = ("-score",)


@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "key", "weight", "updated_at")
    list_filter = ("kind", "updated_at")
    search_fields = ("user__username", "key")
    ordering = ("-weight",)
