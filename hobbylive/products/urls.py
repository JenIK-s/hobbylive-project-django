from django.urls import path
from .views import (
    index, products_list, product_detail,
    profile, order, order_detail,
    wishlist
)

app_name = "products"

urlpatterns = [
    path("", index, name="index"),
    path("products/", products_list, name="products_list"),
    path("product_detail/<int:pk>_id=<int:img_id>", product_detail, name="product_detail"),
    path("profile/", profile, name="profile"),
    path("order/", order, name="order"),
    path("order/<int:pk>", order_detail, name="order_detail"),
    path("wishlist/", wishlist, name="wishlist"),
]
