from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')


def ayuda(request):
    return render(request, 'core/ayuda.html')
