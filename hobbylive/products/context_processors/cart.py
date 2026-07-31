from ..models import Cart


def cart_handler(request):
    if not request.user.is_authenticated:
        return {
            "count": 0,
            "queryset": Cart.objects.none(),
            "total_price": 0,
        }

    queryset = Cart.objects.filter(user=request.user).select_related(
        "product", "image"
    )
    total_price = int(sum(elem.product.price * elem.count for elem in queryset))
    return {
        "count": queryset.count(),
        "queryset": queryset,
        "total_price": total_price,
    }
