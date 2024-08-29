from django import forms
from django.core.exceptions import ValidationError


class QuantityForm(forms.Form):
    qtybutton = forms.IntegerField(
        initial=1,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                'style': 'text-align: center; width: 50px;',
                'id': 'qtybutton',
            }
        )
    )


class OrderForm(forms.Form):
    choises = (
        ("", "Выберите перевозчика"),
        ("СДЭК", "СДЭК"),
        ("ПочтаРоссии", "ПочтаРоссии"),
    )
    first_name = forms.CharField(
        max_length=255,
        label="Имя"
    )
    last_name = forms.CharField(
        max_length=255,
        label="Фамилия"
    )
    address = forms.CharField(
        max_length=1000,
        label="Город доставки"
    )
    phone_number = forms.CharField(
        max_length=255,
        label="Номер телефона"
    )
    carrier = forms.ChoiceField(
        choices=choises,
        widget=forms.Select(),
        label="Служба доставки"
    )

    def clean_carrier(self):
        carrier = self.cleaned_data.get('carrier')
        if carrier == '':
            raise ValidationError('Пожалуйста, выберите перевозчика.')
        return carrier


class AccountDetailForm(forms.Form):
    first_name = forms.CharField(
        max_length=255,
        label="Имя"
    )
    last_name = forms.CharField(
        max_length=255,
        label="Фамилия"
    )
    username = forms.CharField(
        max_length=255,
        label="Логин"
    )
    email = forms.EmailField(
        max_length=255,
        label="Почта"
    )
