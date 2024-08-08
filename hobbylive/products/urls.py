from django.urls import path
from .views import (
    index, products_list, product_detail,
)

app_name = "products"

urlpatterns = [
    path("", index, name="index"),
    path("products/", products_list, name="products_list"),
    path("product_detail/<int:pk>_id=<int:img_id>", product_detail, name="product_detail"),
]
