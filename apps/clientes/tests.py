from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Cliente


class ClienteCrudTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='clave-segura-123')
        self.client.force_login(self.user)
        self.datos = {
            'nombre_completo': 'Ana Torres',
            'cedula': '001-1111111-1',
            'telefono': '8091234567',
            'email': 'ana@test.com',
            'direccion': 'Calle 1',
        }

    def test_crear_cliente(self):
        response = self.client.post(reverse('clientes:crear'), self.datos)
        self.assertRedirects(response, reverse('clientes:index'))
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(Cliente.objects.first().nombre_completo, 'Ana Torres')

    def test_listar_clientes(self):
        Cliente.objects.create(**self.datos)
        response = self.client.get(reverse('clientes:index'))
        self.assertContains(response, 'Ana Torres')

    def test_buscar_cliente(self):
        Cliente.objects.create(**self.datos)
        response = self.client.get(reverse('clientes:index'), {'q': 'Ana'})
        self.assertContains(response, 'Ana Torres')
        response = self.client.get(reverse('clientes:index'), {'q': 'Nadie'})
        self.assertNotContains(response, 'Ana Torres')

    def test_editar_cliente(self):
        cliente = Cliente.objects.create(**self.datos)
        datos_editados = {**self.datos, 'nombre_completo': 'Ana Torres Editada'}
        response = self.client.post(reverse('clientes:editar', args=[cliente.pk]), datos_editados)
        self.assertRedirects(response, reverse('clientes:index'))
        cliente.refresh_from_db()
        self.assertEqual(cliente.nombre_completo, 'Ana Torres Editada')

    def test_eliminar_cliente(self):
        cliente = Cliente.objects.create(**self.datos)
        response = self.client.post(reverse('clientes:eliminar', args=[cliente.pk]))
        self.assertRedirects(response, reverse('clientes:index'))
        self.assertEqual(Cliente.objects.count(), 0)
