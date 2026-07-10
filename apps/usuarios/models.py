from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import TimeStampedModel


class Perfil(TimeStampedModel):
    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        COBRADOR = 'cobrador', 'Cobrador'
        CLIENTE = 'cliente', 'Cliente'

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil'
    )
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.CLIENTE)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.usuario.username} ({self.get_rol_display()})'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        rol = Perfil.Rol.ADMIN if instance.is_superuser else Perfil.Rol.CLIENTE
        Perfil.objects.get_or_create(usuario=instance, defaults={'rol': rol})
