from django.urls import path

from . import views

app_name = 'prestamos'

urlpatterns = [
    path('', views.PrestamoListView.as_view(), name='index'),
    path('nuevo/', views.PrestamoCreateView.as_view(), name='crear'),
    path('<int:pk>/', views.PrestamoDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.PrestamoUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.PrestamoDeleteView.as_view(), name='eliminar'),
]
