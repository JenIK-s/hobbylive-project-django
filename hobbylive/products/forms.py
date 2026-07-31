from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    regex=r"^[\d\s\-\+\(\)]{10,20}$",
    message="Введите корректный номер телефона",
)


class QuantityForm(forms.Form):
    qtybutton = forms.IntegerField(
        initial=1,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "id": "qtybutton",
                "aria-label": "Количество",
            }
        ),
    )


class OrderForm(forms.Form):
    METHOD_PICKUP = "pickup"
    METHOD_DELIVERY = "delivery"
    METHOD_CHOICES = (
        (METHOD_PICKUP, "Самовывоз"),
        (METHOD_DELIVERY, "Доставка"),
    )
    CARRIER_CHOICES = (
        ("", "Выберите службу доставки"),
        ("СДЭК", "СДЭК"),
        ("Почта России", "Почта России"),
        ("Курьер", "Курьер по Москве"),
    )

    delivery_method = forms.ChoiceField(
        choices=METHOD_CHOICES,
        widget=forms.RadioSelect,
        label="Способ получения",
        initial=METHOD_PICKUP,
    )
    first_name = forms.CharField(
        max_length=255,
        label="Имя",
        widget=forms.TextInput(attrs={"placeholder": "Иван", "autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        max_length=255,
        label="Фамилия",
        widget=forms.TextInput(attrs={"placeholder": "Иванов", "autocomplete": "family-name"}),
    )
    phone = forms.CharField(
        max_length=32,
        label="Телефон",
        validators=[phone_validator],
        widget=forms.TextInput(
            attrs={
                "placeholder": "+7 900 000-00-00",
                "autocomplete": "tel",
                "inputmode": "tel",
            }
        ),
    )
    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(
            attrs={"placeholder": "mail@example.com", "autocomplete": "email"}
        ),
    )
    city = forms.CharField(
        required=False,
        max_length=255,
        label="Город",
        widget=forms.TextInput(
            attrs={"placeholder": "Москва", "autocomplete": "address-level2"}
        ),
    )
    street = forms.CharField(
        required=False,
        max_length=255,
        label="Улица",
        widget=forms.TextInput(
            attrs={"placeholder": "ул. Ленина", "autocomplete": "address-line1"}
        ),
    )
    house = forms.CharField(
        required=False,
        max_length=64,
        label="Дом",
        widget=forms.TextInput(attrs={"placeholder": "12"}),
    )
    apartment = forms.CharField(
        required=False,
        max_length=64,
        label="Квартира",
        widget=forms.TextInput(attrs={"placeholder": "45"}),
    )
    entrance = forms.CharField(
        required=False,
        max_length=64,
        label="Подъезд",
        widget=forms.TextInput(attrs={"placeholder": "2"}),
    )
    floor = forms.CharField(
        required=False,
        max_length=64,
        label="Этаж",
        widget=forms.TextInput(attrs={"placeholder": "7"}),
    )
    intercom = forms.CharField(
        required=False,
        max_length=64,
        label="Код домофона",
        widget=forms.TextInput(attrs={"placeholder": "45# или К45"}),
    )
    carrier = forms.ChoiceField(
        required=False,
        choices=CARRIER_CHOICES,
        label="Служба доставки",
    )
    comment = forms.CharField(
        required=False,
        max_length=1000,
        label="Комментарий к заказу",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Удобное время звонка, ориентиры…",
            }
        ),
    )

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get("delivery_method")
        if method == self.METHOD_DELIVERY:
            if not cleaned.get("city"):
                self.add_error("city", "Укажите город")
            if not cleaned.get("street"):
                self.add_error("street", "Укажите улицу")
            if not cleaned.get("house"):
                self.add_error("house", "Укажите дом")
            if not cleaned.get("carrier"):
                self.add_error("carrier", "Выберите службу доставки")
        return cleaned

    @staticmethod
    def format_delivery_address(data):
        parts = [f"г. {data.get('city', '').strip()}".strip()]
        street = data.get("street", "").strip()
        house = data.get("house", "").strip()
        if street or house:
            street_line = street
            if house:
                street_line = f"{street_line}, д. {house}".strip(", ")
            parts.append(street_line)

        details = []
        apartment = data.get("apartment", "").strip()
        entrance = data.get("entrance", "").strip()
        floor = data.get("floor", "").strip()
        intercom = data.get("intercom", "").strip()
        if apartment:
            details.append(f"кв. {apartment}")
        if entrance:
            details.append(f"подъезд {entrance}")
        if floor:
            details.append(f"этаж {floor}")
        if intercom:
            details.append(f"домофон {intercom}")
        if details:
            parts.append(", ".join(details))
        return ", ".join(p for p in parts if p)

    def build_session_payload(self):
        data = self.cleaned_data
        method = data["delivery_method"]
        if method == self.METHOD_PICKUP:
            address = "г. Москва, ул. Артюхиной д. 4"
            carrier = "Самовывоз"
            city = street = house = apartment = entrance = floor = intercom = ""
        else:
            city = data.get("city", "").strip()
            street = data.get("street", "").strip()
            house = data.get("house", "").strip()
            apartment = data.get("apartment", "").strip()
            entrance = data.get("entrance", "").strip()
            floor = data.get("floor", "").strip()
            intercom = data.get("intercom", "").strip()
            address = self.format_delivery_address(
                {
                    "city": city,
                    "street": street,
                    "house": house,
                    "apartment": apartment,
                    "entrance": entrance,
                    "floor": floor,
                    "intercom": intercom,
                }
            )
            carrier = data["carrier"]
        return {
            "delivery_method": method,
            "first_name": data["first_name"].strip(),
            "last_name": data["last_name"].strip(),
            "phone": data["phone"].strip(),
            "email": (data.get("email") or "").strip(),
            "city": city,
            "street": street,
            "house": house,
            "apartment": apartment,
            "entrance": entrance,
            "floor": floor,
            "intercom": intercom,
            "address": address,
            "carrier": carrier,
            "comment": (data.get("comment") or "").strip(),
        }

class AccountDetailForm(forms.Form):
    first_name = forms.CharField(max_length=255, label="Имя")
    last_name = forms.CharField(max_length=255, label="Фамилия")
    username = forms.CharField(max_length=255, label="Логин")
    email = forms.EmailField(max_length=255, label="Почта")
