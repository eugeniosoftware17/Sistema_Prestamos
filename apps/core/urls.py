from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('ayuda/', views.ayuda, name='ayuda'),
    path('buscar/', views.buscar, name='buscar'),
]
