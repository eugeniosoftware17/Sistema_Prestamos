from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from prestamos.models import Prestamo

from .models import Cuota
from .services import generar_cuotas


class RegistrarPagoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='clave-segura-123')
        self.client.force_login(self.user)
        cliente = Cliente.objects.create(
            nombre_completo='Ana Torres', cedula='001-1111111-1', telefono='', email='', direccion=''
        )
        self.prestamo = Prestamo.objects.create(
            cliente=cliente,
            monto=Decimal('12000.00'),
            tasa_interes=Decimal('5'),
            plazo_meses=3,
            fecha_inicio=date(2026, 1, 15),
            estado=Prestamo.Estado.ACTIVO,
        )
        generar_cuotas(self.prestamo)
        self.cuota = self.prestamo.cuotas.get(numero=1)

    def test_registrar_pago_completo_marca_cuota_pagada(self):
        response = self.client.post(
            reverse('pagos:registrar_pago', args=[self.cuota.pk]),
            {'monto_pagado': self.cuota.monto, 'fecha_pago': '2026-02-10', 'metodo': 'Efectivo'},
        )
        self.assertRedirects(response, reverse('pagos:index'))
        self.cuota.refresh_from_db()
        self.assertEqual(self.cuota.estado, Cuota.Estado.PAGADA)
        self.assertEqual(self.cuota.pagos.count(), 1)

    def test_registrar_pago_parcial_no_marca_pagada(self):
        monto_parcial = self.cuota.monto / 2
        self.client.post(
            reverse('pagos:registrar_pago', args=[self.cuota.pk]),
            {'monto_pagado': monto_parcial, 'fecha_pago': '2026-02-10', 'metodo': 'Efectivo'},
        )
        self.cuota.refresh_from_db()
        self.assertEqual(self.cuota.estado, Cuota.Estado.PENDIENTE)
