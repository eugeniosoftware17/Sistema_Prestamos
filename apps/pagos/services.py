import calendar
import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from urllib.parse import quote

from django.conf import settings
from django.core.mail import send_mail

from core.models import ConfiguracionSitio

from .models import Cuota


def _sumar_meses(fecha, meses):
    mes = fecha.month - 1 + meses
    anio = fecha.year + mes // 12
    mes = mes % 12 + 1
    dia = min(fecha.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)


def generar_cuotas(prestamo):
    """Genera las cuotas de un préstamo dividiendo el monto en partes iguales
    según el plazo en meses. La última cuota absorbe el residuo del redondeo."""
    monto_cuota = (prestamo.monto / prestamo.plazo_meses).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_generado = Decimal('0.00')

    for numero in range(1, prestamo.plazo_meses + 1):
        if numero == prestamo.plazo_meses:
            monto = prestamo.monto - total_generado
        else:
            monto = monto_cuota
            total_generado += monto

        Cuota.objects.create(
            prestamo=prestamo,
            numero=numero,
            monto=monto,
            fecha_vencimiento=_sumar_meses(prestamo.fecha_inicio, numero),
        )


def enviar_recibo_por_correo(pago):
    """Envía un correo de confirmación de pago. Devuelve True si se envió
    (o se intentó enviar porque el cliente tiene correo), False si no había
    correo registrado. Nunca lanza excepción (fail_silently)."""
    cliente = pago.cuota.prestamo.cliente
    if not cliente.email:
        return False

    config_sitio = ConfiguracionSitio.cargar()
    asunto = f'Recibo de pago #{pago.pk} - {config_sitio.nombre}'
    cuerpo = (
        f'Hola {cliente.nombre_completo},\n\n'
        f'Confirmamos tu pago de {pago.monto_pagado} correspondiente a la cuota '
        f'N° {pago.cuota.numero} del préstamo #{pago.cuota.prestamo.pk}.\n\n'
        f'Fecha de pago: {pago.fecha_pago}\n'
        f'Método: {pago.metodo or "—"}\n\n'
        f'Gracias por tu pago.\n\n'
        f'{config_sitio.nombre}'
    )
    send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL, [cliente.email], fail_silently=True)
    return True


def generar_link_whatsapp(pago):
    """Arma un enlace wa.me con el mensaje de confirmación de pago ya redactado,
    listo para que el cobrador solo tenga que presionar 'Enviar'. Devuelve None
    si el cliente no tiene teléfono registrado."""
    cliente = pago.cuota.prestamo.cliente
    numero = re.sub(r'\D', '', cliente.telefono or '')
    if not numero:
        return None

    config_sitio = ConfiguracionSitio.cargar()
    mensaje = (
        f'Hola {cliente.nombre_completo}, confirmamos tu pago de {pago.monto_pagado} '
        f'(cuota N° {pago.cuota.numero}, préstamo #{pago.cuota.prestamo.pk}) '
        f'recibido el {pago.fecha_pago}. ¡Gracias! - {config_sitio.nombre}'
    )
    return f'https://wa.me/{numero}?text={quote(mensaje)}'
