from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='usuarios:login'), name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path(
        'perfil/password/',
        auth_views.PasswordChangeView.as_view(
            template_name='usuarios/password_change.html',
            success_url=reverse_lazy('usuarios:password_change_done'),
        ),
        name='password_change',
    ),
    path(
        'perfil/password/hecho/',
        auth_views.PasswordChangeDoneView.as_view(template_name='usuarios/password_change_done.html'),
        name='password_change_done',
    ),
]
