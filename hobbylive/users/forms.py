from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django import forms


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


# class SignInForm(AuthenticationForm):
#     username = forms.CharField(
#         label='Имя пользователя',
#         max_length=150,
#         widget=forms.TextInput(
#             attrs={
#                 'class': 'form-control form-container',
#                 'placeholder': 'Введите ваше имя пользователя',
#                 'id': "floatingInput"
#             }
#         ),
#     )
#     password = forms.CharField(
#         label='Пароль',
#         strip=False,
#         widget=PasswordInput(
#             attrs={
#                 'class': 'form-control form-container',
#                 'placeholder': 'Введите пароль',
#                 'autocomplete': 'new-password'
#             }
#         ),
#     )
#
#     class Meta:
#         model = CustomUser
#         fields = ('username', 'password')
