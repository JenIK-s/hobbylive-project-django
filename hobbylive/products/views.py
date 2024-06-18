from django.shortcuts import render


def index(request):
    count = 2
    return render(request, 'products/index.html', context={'count': count})
