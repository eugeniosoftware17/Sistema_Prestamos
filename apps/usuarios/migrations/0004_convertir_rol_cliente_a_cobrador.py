from django.db import migrations


def convertir_cliente_a_cobrador(apps, schema_editor):
    Perfil = apps.get_model('usuarios', 'Perfil')
    Perfil.objects.filter(rol='cliente').update(rol='cobrador')


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_alter_perfil_rol'),
    ]

    operations = [
        migrations.RunPython(convertir_cliente_a_cobrador, migrations.RunPython.noop),
    ]
