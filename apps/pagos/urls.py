from django.urls import path

from . import views

app_name = 'pagos'

urlpatterns = [
    path('', views.CuotaListView.as_view(), name='index'),
    path('<int:pk>/registrar/', views.registrar_pago, name='registrar_pago'),
    path('pago/<int:pk>/recibo/', views.recibo_pago, name='recibo_pago'),
]
