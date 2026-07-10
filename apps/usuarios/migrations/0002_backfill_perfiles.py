from django.conf import settings
from django.db import migrations


def crear_perfiles_faltantes(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    Perfil = apps.get_model('usuarios', 'Perfil')
    for usuario in User.objects.all():
        rol = 'admin' if usuario.is_superuser else 'cliente'
        Perfil.objects.get_or_create(usuario=usuario, defaults={'rol': rol})


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_perfiles_faltantes, migrations.RunPython.noop),
    ]
