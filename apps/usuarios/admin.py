from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [PerfilInline]


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(Perfil)
