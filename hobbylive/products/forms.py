from django import forms


class QuantityForm(forms.Form):
    qtybutton = forms.IntegerField(initial=1, min_value=1, widget=forms.NumberInput(attrs={
        # 'class': 'cart-plus-minus product-details-quality',
        'style': 'text-align: center; width: 50px;',
        'id': 'qtybutton',
    }))
