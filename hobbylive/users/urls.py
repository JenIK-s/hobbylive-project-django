from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        LogoutView.as_view(),
        name='logout'
    ),
    path(
        'signin/',
        LoginView.as_view(template_name='users/signin.html'),
        name='signin'
    ),
    path('signup/', views.SignUp.as_view(), name='signup'),
]
