from django.shortcuts import render, redirect
from django.db.models import F
from .models import Product, Cart, ProductImage
from .forms import QuantityForm



def index(request):

    return render(request, "products/index.html")


def products_list(request):
    products = Product.objects.all()
    return render(request, "products/products_list.html", {"products": products})


def product_detail(request, pk, img_id):
    product = Product.objects.get(pk=pk)
    form = QuantityForm()
    if request.method == "POST":
        if request.POST.get("image"):
            return redirect("products:product_detail", product.pk, request.POST.get("image"))
        if request.POST.get("action"):
            img = ProductImage.objects.get(pk=img_id)
            if (img_id,) not in Cart.objects.filter(session=request.session.session_key).values_list("image"):
                Cart.objects.create(
                    session=request.session.session_key,
                    product=product,
                    image=img,
                    count=request.POST.get("qtybutton")
                )
            else:
                Cart.objects.filter(image=img).update(count=F("count") + request.POST.get("qtybutton"))
    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "image_large": ProductImage.objects.get(pk=img_id).image.url,
            "form": form
        }
    )
