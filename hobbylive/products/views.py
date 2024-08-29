from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Product, Cart, ProductImage,
    Order, ProductInOrder, Wishlist,
    Categories
)
from .forms import QuantityForm, OrderForm, AccountDetailForm


def index(request):
    return render(request, "products/index.html")


def products_list(request, categories_id):
    queryset = Categories.objects.get(id=categories_id).product.all()
    return render(
        request,
        "products/products_list.html",
        {"products": queryset}
    )


def img_not_in_shop_or_wishlist(img_id: int, user, model) -> bool:
    if (img_id,) not in model.objects.filter(user=user).values_list("image"):
        return True
    return False


def product_detail(request, pk, img_id):
    product = get_object_or_404(Product, pk=pk)
    img = get_object_or_404(ProductImage, pk=img_id)
    heart = determine_heart_icon(request.user, img_id)

    form = QuantityForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(
                "users:signin"
            )

        if request.POST.get("image"):
            return redirect(
                "products:product_detail",
                product.pk,
                request.POST.get("image")
            )

        if request.POST.get("action"):
            handle_cart_action(request, product, img)

        if request.POST.get("add_wishlist"):
            handle_wishlist_action(request, product, img)

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "image_large": img.image.url,
            "form": form,
            "heart": heart,
            "image": img,
        }
    )


def determine_heart_icon(user, img_id):
    return (
        "fa-heart-o"
        if user.is_authenticated and img_not_in_shop_or_wishlist(
            img_id,
            user,
            Wishlist
        ) else "fa-heart"
    )


def handle_cart_action(request, product, img):
    if img_not_in_shop_or_wishlist(img.id, request.user, Cart):
        create_cart_item(request, product, img)
    else:
        update_cart_item(request, img, product)


def create_cart_item(request, product, img):
    data = {
        "user": request.user,
        "product": product,
        "image": img,
        "count": get_cart_count(request, product)
    }
    Cart.objects.create(**data)


def update_cart_item(request, img, product):
    if product.parameters:
        param = request.POST.get("param_value")
        if isinstance(param, int):
            Cart.objects.filter(
                image=img
            ).update(
                parameters_value=F("parameters_value") + param
            )
        else:
            Cart.objects.filter(
                image=img
            ).update(
                count=F("count") + 1
            )
    else:
        Cart.objects.filter(
            image=img
        ).update(
            count=F("count") + request.POST.get("qtybutton")
        )


def get_cart_count(request, product):
    if product.parameters:
        param = request.POST.get("param_value")
        return int(param) // int(
            product.parameters_value.all()[0].value
        ) if param.isdigit() else 1
    return request.POST.get("qtybutton")


def handle_wishlist_action(request, product, img):
    if img_not_in_shop_or_wishlist(img.id, request.user, Wishlist):
        Wishlist.objects.create(user=request.user, product=product, image=img)
    else:
        Wishlist.objects.filter(user=request.user, image=img).delete()


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
    return render(
        request,
        "products/profile.html",
        {
            "orders": orders,
            "form": form,
            "orders_staff": Order.objects.all()
        }
    )


def create_order(user, address, carrier):
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
    try:
        for elem in queryset:
            data = {
                "user": user,
                "product": elem.product,
                "image": elem.image,
                "count": elem.count
            }
            if elem.product.parameters:
                data.update(
                    {
                        "parameters": elem.parameters,
                        "parameters_value": elem.parameter_value,
                    }
                )
            product = ProductInOrder.objects.create(**data)
            user_order.products.add(product)
        user_order.save()
        queryset.delete()
    except:
        user_order.delete()
        raise ValidationError("Заказ должен содержать хотя бы один товар")


@login_required
def order(request):
    data = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name
    }
    form = OrderForm(data)
    if request.method == "POST":
        print("POST")
        if request.POST.get("to_order"):
            print("to_order")
            form = OrderForm(request.POST)
            if form.is_valid():
                data = {
                    "address": request.POST.get("address"),
                    "carrier": request.POST.get("carrier")
                }
                request.session['data'] = data
                return redirect("products:order_accept")
        elif request.POST.get("to_order_pickup"):
            data = {
                "address": "г. Москва, ул. Артюхиной д. 4",
                "carrier": "Самовывоз"
            }
            request.session['data'] = data
            return redirect("products:order_accept")

    return render(
        request,
        "products/order.html",
        {
            "form": form
        }
    )


@login_required
def order_accept(request):
    data = request.session.get("data")
    queryset = Cart.objects.filter(user=request.user)
    total_price = 0
    for elem in queryset:
        total_price += elem.product.price * elem.count
    if request.method == "POST":
        create_order(request.user, data.get("address"), data.get("carrier"))
        return redirect("products:profile")
    return render(
        request,
        "products/order_accept.html",
        {
            "data": data,
            "products": queryset,
            "total_price": total_price
        }
    )


@login_required
def order_detail(request, pk):
    user_order = Order.objects.filter(pk=pk)
    if request.method == "POST":
        user_order.delete()
        return redirect("products:profile")
    return render(
        request,
        "products/order_detail.html",
        {
            "order": user_order[0]
        }
    )


@login_required
def wishlist(request):
    user_wishlist = Wishlist.objects.filter(user=request.user)
    if request.method == "POST":
        if request.POST.get("action"):
            pk = request.POST.get("action")
            wishlist_elem = Wishlist.objects.filter(pk=pk)
            if img_not_in_shop_or_wishlist(
                    wishlist_elem[0].image.id,
                    request.user,
                    Cart
            ):
                Cart.objects.create(
                    user=request.user,
                    product=wishlist_elem[0].product,
                    image=wishlist_elem[0].image,
                    count=1
                )
            else:
                Cart.objects.filter(
                    image=wishlist_elem[0].image
                ).update(count=F("count") + 1)
        else:
            pk = request.POST.get("pk_w")
        Wishlist.objects.filter(pk=pk).delete()
    return render(
        request,
        "products/wishlist.html",
        {
            "wishlist": user_wishlist
        }
    )


def categories(request):
    queryset = Categories.objects.all()
    return render(
        request,
        "products/categories.html",
        {
            "categories": queryset
        }
    )
