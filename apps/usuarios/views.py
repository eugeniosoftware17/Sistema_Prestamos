from django.contrib import messages
from django.shortcuts import redirect, render

from core.forms import ConfiguracionSitioForm
from core.models import ConfiguracionSitio


def perfil(request):
    return render(request, 'usuarios/perfil.html')


def configuracion(request):
    config = ConfiguracionSitio.cargar()

    if request.method == 'POST':
        form = ConfiguracionSitioForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración actualizada correctamente.')
            return redirect('usuarios:configuracion')
    else:
        form = ConfiguracionSitioForm(instance=config)

    return render(request, 'usuarios/configuracion.html', {'form': form, 'config': config})
