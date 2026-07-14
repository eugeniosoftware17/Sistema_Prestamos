from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Perfil


class PerfilSignalTests(TestCase):
    def test_crear_usuario_normal_asigna_rol_cobrador(self):
        user = get_user_model().objects.create_user(username='empleado1', password='clave-segura-123')
        self.assertTrue(hasattr(user, 'perfil'))
        self.assertEqual(user.perfil.rol, Perfil.Rol.COBRADOR)

    def test_crear_superusuario_asigna_rol_admin(self):
        user = get_user_model().objects.create_superuser(
            username='jefe1', password='clave-segura-123', email='jefe1@test.com'
        )
        self.assertEqual(user.perfil.rol, Perfil.Rol.ADMIN)

    def test_no_duplica_perfil_al_guardar_de_nuevo(self):
        user = get_user_model().objects.create_user(username='empleado2', password='clave-segura-123')
        user.email = 'empleado2@test.com'
        user.save()
        self.assertEqual(Perfil.objects.filter(usuario=user).count(), 1)


class ConfiguracionViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='clave-segura-123')
        self.client.force_login(self.user)

    def test_actualizar_nombre_del_sitio(self):
        response = self.client.post(
            reverse('usuarios:configuracion'), {'nombre': 'Mi Sistema', 'diseno_recibo': 'formal'}
        )
        self.assertRedirects(response, reverse('usuarios:configuracion'))

        from core.models import ConfiguracionSitio
        self.assertEqual(ConfiguracionSitio.cargar().nombre, 'Mi Sistema')
