from ..models import Cart


def cart_handler(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        Cart.objects.filter(pk=pk).delete()

    queryset = Cart.objects.filter(session=request.session.session_key)
    total_price = 0
    for elem in queryset:
        total_price += elem.product.price * elem.count

    return {"count": len(queryset), "queryset": queryset, "total_price": total_price}
