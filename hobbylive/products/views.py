from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Product, Cart, ProductImage,
    Order, ProductInOrder, Wishlist,
    Categories
)
from .forms import QuantityForm, OrderForm, AccountDetailForm
from .recommendations import (
    get_personalized_products,
    get_popular_products,
    get_related_products,
    track_cart_add,
    track_product_view,
    track_purchase,
    track_search,
    track_wishlist_add,
)


def index(request):
    return render(
        request,
        "products/index.html",
        {
            "popular_products": get_popular_products(limit=8),
        },
    )


def popular(request):
    products = get_popular_products(limit=24)
    return render(
        request,
        "products/popular.html",
        {"products": products},
    )


def search(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.none()
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).prefetch_related("images", "Categories")
        track_search(request.user, query, list(products[:12]))
    return render(
        request,
        "products/search.html",
        {"products": products, "query": query},
    )


def products_list(request, categories_id):
    category = get_object_or_404(Categories, id=categories_id)
    products = category.product.prefetch_related("images").all()
    return render(
        request,
        "products/products_list.html",
        {"products": products, "category": category},
    )


def img_not_in_shop_or_wishlist(img_id: int, user, model) -> bool:
    return not model.objects.filter(user=user, image_id=img_id).exists()


def product_detail(request, pk, img_id):
    product = get_object_or_404(Product, pk=pk)
    img = get_object_or_404(ProductImage, pk=img_id, product=product)
    form = QuantityForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("users:signin")

        selected = request.POST.get("selected_image") or request.POST.get("image")
        if selected:
            img = get_object_or_404(ProductImage, pk=selected, product=product)

        if request.POST.get("action"):
            handle_cart_action(request, product, img)
            messages.success(request, "Товар добавлен в корзину")

        if request.POST.get("add_wishlist"):
            handle_wishlist_action(request, product, img)

        return redirect("products:product_detail", product.pk, img.pk)

    heart = determine_heart_icon(request.user, img.pk)
    track_product_view(request.user, product)
    related_products = get_related_products(product, limit=8)

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "image_large": img.image.url,
            "form": form,
            "heart": heart,
            "image": img,
            "related_products": related_products,
        },
    )


def determine_heart_icon(user, img_id):
    if not user.is_authenticated:
        return "fa-heart-o"
    if img_not_in_shop_or_wishlist(img_id, user, Wishlist):
        return "fa-heart-o"
    return "fa-heart"


def handle_cart_action(request, product, img):
    if img_not_in_shop_or_wishlist(img.id, request.user, Cart):
        create_cart_item(request, product, img)
    else:
        update_cart_item(request, img, product)
    track_cart_add(request.user, product)


def _safe_int(value, default=1):
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return default


def create_cart_item(request, product, img):
    data = {
        "user": request.user,
        "product": product,
        "image": img,
        "count": get_cart_count(request, product),
    }
    if product.parameters:
        data["parameters"] = product.parameters
        data["parameters_value"] = request.POST.get("param_value", "")
        data["measurement_unit"] = product.measurement_unit
    Cart.objects.create(**data)


def update_cart_item(request, img, product):
    cart_qs = Cart.objects.filter(user=request.user, image=img)
    qty = _safe_int(request.POST.get("qtybutton"))
    if product.parameters:
        param = request.POST.get("param_value", "")
        # same image + same param → bump qty; otherwise just update param
        existing = cart_qs.filter(parameters_value=param).first() if param else None
        if existing:
            cart_qs.filter(pk=existing.pk).update(count=F("count") + qty)
        else:
            cart_qs.update(
                parameters_value=param,
                count=F("count") + qty,
            )
    else:
        cart_qs.update(count=F("count") + qty)


def get_cart_count(request, product):
    return _safe_int(request.POST.get("qtybutton"))


def handle_wishlist_action(request, product, img):
    if img_not_in_shop_or_wishlist(img.id, request.user, Wishlist):
        Wishlist.objects.create(user=request.user, product=product, image=img)
        track_wishlist_add(request.user, product)
        messages.success(request, "Добавлено в избранное")
    else:
        Wishlist.objects.filter(user=request.user, image=img).delete()
        messages.success(request, "Удалено из избранного")


@login_required
def cart_remove(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        Cart.objects.filter(pk=pk, user=request.user).delete()
        messages.success(request, "Товар удалён из корзины")
    return redirect(request.META.get("HTTP_REFERER", "products:index"))


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by("-date")
    data = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
        "username": request.user.username,
    }
    form = AccountDetailForm(initial=data)
    if request.method == "POST":
        form = AccountDetailForm(request.POST)
        if form.is_valid():
            User = get_user_model()
            User.objects.filter(id=request.user.id).update(
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                username=form.cleaned_data["username"],
            )
            messages.success(request, "Данные аккаунта успешно сохранены")
            return redirect("products:profile")
    context = {
        "orders": orders,
        "form": form,
        "recommended_products": get_personalized_products(request.user, limit=8),
    }
    if request.user.is_staff:
        context["orders_staff"] = Order.objects.select_related("user").order_by("-date")
    return render(request, "products/profile.html", context)


def create_order(user, address, carrier):
    queryset = Cart.objects.filter(user=user).select_related("product", "image")
    if not queryset.exists():
        raise ValueError("Корзина пуста")

    total_price = int(sum(elem.product.price * elem.count for elem in queryset))

    with transaction.atomic():
        user_order = Order.objects.create(
            user=user,
            address=address,
            total_price=total_price,
            carrier=carrier,
        )
        purchased_products = []
        for elem in queryset:
            data = {
                "user": user,
                "product": elem.product,
                "image": elem.image,
                "count": elem.count,
            }
            if elem.product.parameters:
                data.update(
                    {
                        "parameters": elem.parameters,
                        "parameters_value": elem.parameters_value,
                        "measurement_unit": elem.measurement_unit,
                    }
                )
            product_in_order = ProductInOrder.objects.create(**data)
            user_order.products.add(product_in_order)
            purchased_products.append(elem.product)
        queryset.delete()
    track_purchase(user, purchased_products)
    return user_order


@login_required
def order(request):
    cart = Cart.objects.filter(user=request.user)
    if not cart.exists():
        messages.warning(request, "Корзина пуста — добавьте товары перед оформлением")
        return redirect("products:categories")

    form = OrderForm(
        initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }
    )
    if request.method == "POST":
        if request.POST.get("to_order"):
            form = OrderForm(request.POST)
            if form.is_valid():
                request.session["data"] = {
                    "address": form.cleaned_data["address"],
                    "carrier": form.cleaned_data["carrier"],
                    "phone_number": form.cleaned_data["phone_number"],
                }
                return redirect("products:order_accept")
        elif request.POST.get("to_order_pickup"):
            request.session["data"] = {
                "address": "г. Москва, ул. Артюхиной д. 4",
                "carrier": "Самовывоз",
                "phone_number": "",
            }
            return redirect("products:order_accept")

    return render(request, "products/order.html", {"form": form})


@login_required
def order_accept(request):
    data = request.session.get("data")
    if not data:
        return redirect("products:order")

    queryset = Cart.objects.filter(user=request.user).select_related("product", "image")
    if not queryset.exists():
        messages.warning(request, "Корзина пуста")
        return redirect("products:categories")

    total_price = int(sum(elem.product.price * elem.count for elem in queryset))

    if request.method == "POST":
        try:
            create_order(request.user, data.get("address"), data.get("carrier"))
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("products:categories")
        request.session.pop("data", None)
        messages.success(
            request,
            "Заказ успешно оформлен! Мы свяжемся с вами в ближайшее время.",
        )
        return redirect("products:profile")

    return render(
        request,
        "products/order_accept.html",
        {
            "data": data,
            "products": queryset,
            "total_price": total_price,
        },
    )


@login_required
def order_detail(request, pk):
    order_obj = get_object_or_404(Order, pk=pk)
    if order_obj.user != request.user and not request.user.is_staff:
        raise Http404

    cancellable_statuses = {"Создан", "Собирается"}
    can_cancel = (
        (order_obj.user == request.user or request.user.is_staff)
        and order_obj.status in cancellable_statuses
    )

    if request.method == "POST":
        if can_cancel:
            order_obj.status = "Отменен"
            order_obj.save(update_fields=["status"])
            messages.success(request, "Заказ отменён")
        else:
            messages.error(request, "Этот заказ нельзя отменить")
        return redirect("products:order_detail", order_obj.pk)

    items = order_obj.products.select_related("product", "image").all()
    return render(
        request,
        "products/order_detail.html",
        {
            "order": order_obj,
            "items": items,
            "total_price": order_obj.total_price,
            "can_cancel": can_cancel,
        },
    )


@login_required
def wishlist(request):
    user_wishlist = Wishlist.objects.filter(user=request.user).select_related(
        "product", "image"
    )
    if request.method == "POST":
        if request.POST.get("action"):
            pk = request.POST.get("action")
            item = get_object_or_404(Wishlist, pk=pk, user=request.user)
            if img_not_in_shop_or_wishlist(item.image.id, request.user, Cart):
                Cart.objects.create(
                    user=request.user,
                    product=item.product,
                    image=item.image,
                    count=1,
                )
            else:
                Cart.objects.filter(user=request.user, image=item.image).update(
                    count=F("count") + 1
                )
            track_cart_add(request.user, item.product)
            messages.success(request, "Товар добавлен в корзину")
        elif request.POST.get("pk_w"):
            Wishlist.objects.filter(
                pk=request.POST.get("pk_w"), user=request.user
            ).delete()
            messages.success(request, "Удалено из избранного")
    return render(request, "products/wishlist.html", {"wishlist": user_wishlist})


def categories(request):
    return render(
        request,
        "products/categories.html",
        {"categories": Categories.objects.all()},
    )
