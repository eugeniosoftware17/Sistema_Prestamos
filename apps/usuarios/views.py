from django.shortcuts import render


def perfil(request):
    return render(request, 'usuarios/perfil.html')


def configuracion(request):
    return render(request, 'usuarios/configuracion.html')
