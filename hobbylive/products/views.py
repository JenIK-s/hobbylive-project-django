from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render, redirect
from .models import (
    Product, Cart, ProductImage,
    Order, ProductInOrder, Wishlist
)
from .forms import QuantityForm, OrderForm
from django.contrib import messages


def index(request):
    return render(request, "products/index.html")


def products_list(request):
    return render(request, "products/products_list.html")


def img_not_in_shop_or_wishlist(img_id: int, user, model) -> bool:
    if (img_id,) not in model.objects.filter(user=user).values_list("image"):
        return True
    return False


def product_detail(request, pk, img_id):
    product = Product.objects.get(pk=pk)
    img = ProductImage.objects.get(pk=img_id)
    heart = "fa-heart"
    if request.user.is_authenticated:
        if img_not_in_shop_or_wishlist(img_id, request.user, Wishlist):
            heart = "fa-heart-o"
    form = QuantityForm()
    if request.method == "POST":
        if request.POST.get("image"):
            return redirect("products:product_detail", product.pk, request.POST.get("image"))
        elif request.POST.get("action"):
            if request.user.is_authenticated:
                if img_not_in_shop_or_wishlist(img_id, request.user, Cart):
                    Cart.objects.create(
                        user=request.user,
                        product=product,
                        image=img,
                        count=request.POST.get("qtybutton")
                    )
                else:
                    Cart.objects.filter(image=img).update(count=F("count") + request.POST.get("qtybutton"))
        elif request.POST.get("add_wishlist"):
            if img_not_in_shop_or_wishlist(img_id, request.user, Wishlist):
                Wishlist.objects.create(
                    user=request.user,
                    product=product,
                    image=img,
                )
            else:
                Wishlist.objects.filter(user=request.user, image=img).delete()
    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "image_large": ProductImage.objects.get(pk=img_id).image.url,
            "form": form,
            "heart": heart,
        }
    )


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "products/profile.html", {"orders": orders})


@login_required
def order(request):
    data = {"first_name": request.user.first_name, "last_name": request.user.last_name}
    form = OrderForm(data)
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            queryset = Cart.objects.filter(user=request.user)
            total_price = 0
            for elem in queryset:
                total_price += elem.product.price * elem.count
            user_order = Order.objects.create(
                user=request.user,
                address=request.POST.get('address'),
                total_price=total_price,
                carrier=request.POST.get('carrier')
            )
            for elem in queryset:
                product = ProductInOrder.objects.create(
                    user=request.user,
                    product=elem.product,
                    image=elem.image,
                    count=elem.count
                )
                user_order.products.add(product)
            user_order.save()
            queryset.delete()
            messages.success(request, "Заказ успешно оформлен")
        else:
            messages.error(request, "Заказ не был оформлен")
    return render(request, "products/order.html", {"form": form})


@login_required
def order_detail(request, pk):
    user_order = Order.objects.get(pk=pk)
    return render(request, "products/order_detail.html", {"order": user_order})


@login_required
def wishlist(request):
    user_wishlist = Wishlist.objects.filter(user=request.user)
    if request.method == "POST":
        pk = request.POST.get("pk_w")
        Wishlist.objects.filter(pk=pk).delete()
    return render(request, "products/wishlist.html", {"wishlist": user_wishlist})
