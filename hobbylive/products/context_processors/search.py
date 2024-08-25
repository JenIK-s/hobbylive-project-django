from django.db.models.functions import Lower
from django.db.models import Q

from ..models import Product


def search_handler(request):
    if request.method == "GET" and request.GET.get("q"):
        products = Product.objects.filter(Q(name__contains=request.GET.get("q")))
    else:
        products = Product.objects.all()
    return {"products": products}
