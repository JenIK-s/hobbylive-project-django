from django.shortcuts import redirect

from ..models import Cart


def cart_handler(request):
    if request.user.is_authenticated:
        if request.method == "POST" and request.POST.get("pk"):
            pk = request.POST.get("pk")
            Cart.objects.filter(pk=pk).delete()

        queryset = Cart.objects.filter(user=request.user)
        total_price = 0
        for elem in queryset:
            total_price += elem.product.price * elem.count

        return {"count": len(queryset), "queryset": queryset, "total_price": total_price}
    return []
