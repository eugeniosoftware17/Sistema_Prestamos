from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from pagos.models import Cuota

from .models import Prestamo


class PrestamoCrudTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='clave-segura-123')
        self.client.force_login(self.user)
        self.cliente = Cliente.objects.create(
            nombre_completo='Ana Torres', cedula='001-1111111-1', telefono='', email='', direccion=''
        )
        self.datos = {
            'cliente': self.cliente.pk,
            'monto': '12000.00',
            'tasa_interes': '5',
            'plazo_meses': '3',
            'fecha_inicio': '2026-01-15',
            'estado': Prestamo.Estado.ACTIVO,
        }

    def test_crear_prestamo_genera_cuotas(self):
        response = self.client.post(reverse('prestamos:crear'), self.datos)
        self.assertRedirects(response, reverse('prestamos:index'))
        prestamo = Prestamo.objects.get()

        cuotas = list(prestamo.cuotas.order_by('numero'))
        self.assertEqual(len(cuotas), 3)
        self.assertEqual(sum(c.monto for c in cuotas), Decimal('12000.00'))
        self.assertEqual(cuotas[0].fecha_vencimiento.isoformat(), '2026-02-15')
        self.assertEqual(cuotas[1].fecha_vencimiento.isoformat(), '2026-03-15')
        self.assertEqual(cuotas[2].fecha_vencimiento.isoformat(), '2026-04-15')

    def test_eliminar_prestamo_sin_pagos(self):
        self.client.post(reverse('prestamos:crear'), self.datos)
        prestamo = Prestamo.objects.get()
        response = self.client.post(reverse('prestamos:eliminar', args=[prestamo.pk]))
        self.assertRedirects(response, reverse('prestamos:index'))
        self.assertEqual(Prestamo.objects.count(), 0)
        self.assertEqual(Cuota.objects.count(), 0)

    def test_eliminar_prestamo_con_pago_falla_con_mensaje(self):
        self.client.post(reverse('prestamos:crear'), self.datos)
        prestamo = Prestamo.objects.get()
        cuota = prestamo.cuotas.first()
        cuota.pagos.create(monto_pagado=cuota.monto, fecha_pago='2026-02-10')

        response = self.client.post(reverse('prestamos:eliminar', args=[prestamo.pk]), follow=True)
        self.assertEqual(Prestamo.objects.count(), 1)
        mensajes = [str(m) for m in response.context['messages']]
        self.assertTrue(any('no se puede eliminar' in m.lower() for m in mensajes))

    def test_editar_prestamo_sin_pagos_regenera_cuotas(self):
        self.client.post(reverse('prestamos:crear'), self.datos)
        prestamo = Prestamo.objects.get()

        datos_editados = {**self.datos, 'monto': '6000.00', 'plazo_meses': '2'}
        response = self.client.post(reverse('prestamos:editar', args=[prestamo.pk]), datos_editados)
        self.assertRedirects(response, reverse('prestamos:index'))

        cuotas = list(prestamo.cuotas.order_by('numero'))
        self.assertEqual(len(cuotas), 2)
        self.assertEqual(sum(c.monto for c in cuotas), Decimal('6000.00'))

    def test_editar_prestamo_con_pagos_no_toca_cuotas(self):
        self.client.post(reverse('prestamos:crear'), self.datos)
        prestamo = Prestamo.objects.get()
        cuota = prestamo.cuotas.first()
        cuota.pagos.create(monto_pagado=cuota.monto, fecha_pago='2026-02-10')

        datos_editados = {**self.datos, 'monto': '6000.00', 'plazo_meses': '2'}
        response = self.client.post(
            reverse('prestamos:editar', args=[prestamo.pk]), datos_editados, follow=True
        )
        self.assertEqual(prestamo.cuotas.count(), 3)
        mensajes = [str(m) for m in response.context['messages']]
        self.assertTrue(any('no se regeneraron' in m.lower() for m in mensajes))
