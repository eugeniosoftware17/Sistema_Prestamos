from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from prestamos.models import Prestamo

from .models import Cuota
from .services import (
    enviar_recibo_por_correo,
    generar_cuotas,
    generar_link_bluetooth_print,
    generar_link_whatsapp,
)


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


class CuotaListViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester2', password='clave-segura-123')
        self.client.force_login(self.user)

        cliente_a = Cliente.objects.create(
            nombre_completo='Ana Torres', cedula='001-1111111-1', telefono='', email='', direccion=''
        )
        cliente_b = Cliente.objects.create(
            nombre_completo='Beto Ruiz', cedula='002-2222222-2', telefono='', email='', direccion=''
        )

        prestamo_a = Prestamo.objects.create(
            cliente=cliente_a, monto=Decimal('1000.00'), tasa_interes=Decimal('5'),
            plazo_meses=1, fecha_inicio=date(2020, 1, 1), estado=Prestamo.Estado.ACTIVO,
        )
        generar_cuotas(prestamo_a)

        prestamo_b = Prestamo.objects.create(
            cliente=cliente_b, monto=Decimal('1000.00'), tasa_interes=Decimal('5'),
            plazo_meses=1, fecha_inicio=date(2030, 1, 1), estado=Prestamo.Estado.ACTIVO,
        )
        generar_cuotas(prestamo_b)

    def test_buscar_por_cliente(self):
        response = self.client.get(reverse('pagos:index'), {'q': 'Ana'})
        self.assertContains(response, 'Ana Torres')
        self.assertNotContains(response, 'Beto Ruiz')

    def test_filtrar_vencidas(self):
        response = self.client.get(reverse('pagos:index'), {'estado': 'vencida'})
        self.assertContains(response, 'Ana Torres')
        self.assertNotContains(response, 'Beto Ruiz')


class ReciboPagoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester3', password='clave-segura-123')
        self.client.force_login(self.user)
        cliente = Cliente.objects.create(
            nombre_completo='Ana Torres', cedula='001-1111111-1', telefono='', email='', direccion=''
        )
        prestamo = Prestamo.objects.create(
            cliente=cliente, monto=Decimal('1000.00'), tasa_interes=Decimal('5'),
            plazo_meses=1, fecha_inicio=date(2026, 1, 1), estado=Prestamo.Estado.ACTIVO,
        )
        generar_cuotas(prestamo)
        cuota = prestamo.cuotas.get(numero=1)
        self.pago = cuota.pagos.create(monto_pagado=cuota.monto, fecha_pago=date(2026, 1, 5))

    def test_primera_vez_dice_original(self):
        response = self.client.get(reverse('pagos:recibo_pago', args=[self.pago.pk]))
        self.assertContains(response, 'ORIGINAL')
        self.pago.refresh_from_db()
        self.assertTrue(self.pago.impreso)

    def test_segunda_vez_dice_copia(self):
        self.client.get(reverse('pagos:recibo_pago', args=[self.pago.pk]))
        response = self.client.get(reverse('pagos:recibo_pago', args=[self.pago.pk]))
        self.assertContains(response, 'COPIA')
        self.assertNotContains(response, 'ORIGINAL')

    def test_usa_el_diseno_configurado(self):
        from core.models import ConfiguracionSitio

        config = ConfiguracionSitio.cargar()
        config.diseno_recibo = ConfiguracionSitio.DisenoRecibo.TICKET
        config.save()

        response = self.client.get(reverse('pagos:recibo_pago', args=[self.pago.pk]))
        self.assertTemplateUsed(response, 'pagos/recibo_ticket.html')


class NotificacionesPagoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester4', password='clave-segura-123')
        self.client.force_login(self.user)

    def _crear_pago(self, email='', telefono=''):
        cliente = Cliente.objects.create(
            nombre_completo='Ana Torres', cedula='001-1111111-1', telefono=telefono, email=email, direccion=''
        )
        prestamo = Prestamo.objects.create(
            cliente=cliente, monto=Decimal('1000.00'), tasa_interes=Decimal('5'),
            plazo_meses=1, fecha_inicio=date(2026, 1, 1), estado=Prestamo.Estado.ACTIVO,
        )
        generar_cuotas(prestamo)
        cuota = prestamo.cuotas.get(numero=1)
        return cuota.pagos.create(monto_pagado=cuota.monto, fecha_pago=date(2026, 1, 5))

    def test_enviar_correo_con_email_registrado(self):
        pago = self._crear_pago(email='ana@test.com')
        enviado = enviar_recibo_por_correo(pago)
        self.assertTrue(enviado)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('ana@test.com', mail.outbox[0].to)

    def test_no_envia_correo_sin_email(self):
        pago = self._crear_pago(email='')
        enviado = enviar_recibo_por_correo(pago)
        self.assertFalse(enviado)
        self.assertEqual(len(mail.outbox), 0)

    def test_link_whatsapp_con_telefono(self):
        pago = self._crear_pago(telefono='(809) 555-1234')
        link = generar_link_whatsapp(pago)
        self.assertIsNotNone(link)
        self.assertTrue(link.startswith('https://wa.me/8095551234'))

    def test_link_whatsapp_sin_telefono(self):
        pago = self._crear_pago(telefono='')
        link = generar_link_whatsapp(pago)
        self.assertIsNone(link)

    def test_link_bluetooth_print_original(self):
        pago = self._crear_pago()
        link = generar_link_bluetooth_print(pago, es_copia=False)
        self.assertTrue(link.startswith('intent://send/#Intent;'))
        self.assertIn('package=mate.bluetoothprint', link)
        self.assertIn('ORIGINAL', link)

    def test_link_bluetooth_print_copia(self):
        pago = self._crear_pago()
        link = generar_link_bluetooth_print(pago, es_copia=True)
        self.assertIn('COPIA', link)

    def test_registrar_pago_envia_correo_automaticamente(self):
        cliente = Cliente.objects.create(
            nombre_completo='Beto Ruiz', cedula='002-2222222-2', telefono='', email='beto@test.com', direccion=''
        )
        prestamo = Prestamo.objects.create(
            cliente=cliente, monto=Decimal('1000.00'), tasa_interes=Decimal('5'),
            plazo_meses=1, fecha_inicio=date(2026, 1, 1), estado=Prestamo.Estado.ACTIVO,
        )
        generar_cuotas(prestamo)
        cuota = prestamo.cuotas.get(numero=1)

        self.client.post(
            reverse('pagos:registrar_pago', args=[cuota.pk]),
            {'monto_pagado': cuota.monto, 'fecha_pago': '2026-02-10', 'metodo': 'Efectivo'},
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('beto@test.com', mail.outbox[0].to)
