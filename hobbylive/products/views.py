from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render, redirect
from .models import (
    Product, Cart, ProductImage,
    Order, ProductInOrder, Wishlist,
    Categories
)
from .forms import QuantityForm, OrderForm, AccountDetailForm
from django.contrib import messages


def index(request):
    return render(request, "products/index.html")


def products_list(request, categories_id):
    queryset = Categories.objects.get(id=categories_id).product.all()
    return render(request, "products/products_list.html", {"products": queryset})


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
            else:
                return redirect("users:signin")
        elif request.POST.get("add_wishlist"):
            if request.user.is_authenticated:
                if img_not_in_shop_or_wishlist(img_id, request.user, Wishlist):
                    Wishlist.objects.create(
                        user=request.user,
                        product=product,
                        image=img,
                    )
                else:
                    Wishlist.objects.filter(user=request.user, image=img).delete()
            else:
                return redirect("users:signin")
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
    data = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
        "username": request.user.username
    }
    form = AccountDetailForm(initial=data)
    if request.method == "POST":
        form = AccountDetailForm(request.POST)
        if form.is_valid():
            data = {
                "first_name": form.data["first_name"],
                "last_name": form.data["last_name"],
                "email": form.data["email"],
                "username": form.data["username"]
            }
            User = get_user_model()
            User.objects.filter(id=request.user.id).update(**data)
    return render(request, "products/profile.html", {"orders": orders, "form": form})


def create_order(user, address="г. Москва, ул. Артюхиной д. 4", carrier="Самовывоз"):
    queryset = Cart.objects.filter(user=user)
    total_price = 0
    for elem in queryset:
        total_price += elem.product.price * elem.count
    user_order = Order.objects.create(
        user=user,
        address=address,
        total_price=total_price,
        carrier=carrier
    )
    for elem in queryset:
        product = ProductInOrder.objects.create(
            user=user,
            product=elem.product,
            image=elem.image,
            count=elem.count
        )
        user_order.products.add(product)
    user_order.save()
    queryset.delete()


@login_required
def order(request):
    data = {"first_name": request.user.first_name, "last_name": request.user.last_name}
    form = OrderForm(data)
    if request.method == "POST":
        print("POST")
        if request.POST.get("to_order"):
            print("to_order")
            form = OrderForm(request.POST)
            if form.is_valid():
                create_order(request.user, request.POST.get("address"), request.POST.get("carrier"))
                messages.success(request, "Заказ успешно оформлен")
        elif request.POST.get("to_order_pickup"):
            print("to_order_pickup")
            create_order(request.user)
            messages.success(request, "Заказ успешно оформлен")

        # else:
        #     messages.error(request, "Заказ не был оформлен")
    return render(request, "products/order.html", {"form": form})


@login_required
def order_detail(request, pk):
    user_order = Order.objects.filter(pk=pk)
    if request.method == "POST":
        user_order.delete()
        return redirect("products:profile")
    return render(request, "products/order_detail.html", {"order": user_order[0]})


@login_required
def wishlist(request):
    user_wishlist = Wishlist.objects.filter(user=request.user)
    if request.method == "POST":
        if request.POST.get("action"):
            pk = request.POST.get("action")
            wishlist_elem = Wishlist.objects.filter(pk=pk)
            if img_not_in_shop_or_wishlist(wishlist_elem[0].image.id, request.user, Cart):
                Cart.objects.create(
                    user=request.user,
                    product=wishlist_elem[0].product,
                    image=wishlist_elem[0].image,
                    count=1
                )
            else:
                Cart.objects.filter(image=wishlist_elem[0].image).update(count=F("count") + 1)
        else:
            pk = request.POST.get("pk_w")
        Wishlist.objects.filter(pk=pk).delete()
    return render(request, "products/wishlist.html", {"wishlist": user_wishlist})


def categories(request):
    queryset = Categories.objects.all()
    return render(request, "products/categories.html", {"categories": queryset})
