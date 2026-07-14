from django import forms

from .models import ConfiguracionSitio


class ConfiguracionSitioForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionSitio
        fields = ['nombre', 'icono', 'direccion', 'telefono', 'rnc', 'email', 'diseno_recibo']
