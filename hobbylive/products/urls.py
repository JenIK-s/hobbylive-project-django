from django.urls import path
from .views import (
    index
)

app_name = "products"

urlpatterns = [
    path("", index, name="index")
]
