from django import forms

from .models import Pago


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['monto_pagado', 'fecha_pago', 'metodo']
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
        }
