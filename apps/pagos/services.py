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


def _texto_ticket_bluetooth_print(pago, es_copia):
    """Arma el contenido del recibo con el formato de etiquetas que usa la
    app 'Bluetooth Print' (mate.bluetoothprint): <BAF>Texto, donde
    B=negrita(0/1), A=alineación(0 izq/1 centro/2 der), F=tamaño(0 normal/
    1 alto doble/2 alto+ancho doble/3 ancho doble)."""
    config_sitio = ConfiguracionSitio.cargar()
    cliente = pago.cuota.prestamo.cliente
    sello = 'COPIA' if es_copia else 'ORIGINAL'

    lineas = [f'<113>{config_sitio.nombre}']
    if config_sitio.direccion:
        lineas.append(f'<101>{config_sitio.direccion}')
    contacto = []
    if config_sitio.telefono:
        contacto.append(f'Tel: {config_sitio.telefono}')
    if config_sitio.rnc:
        contacto.append(f'RNC: {config_sitio.rnc}')
    if contacto:
        lineas.append(f'<101>{" - ".join(contacto)}')

    lineas.append(f'<111>*** {sello} ***')
    lineas.append('<100>--------------------------------')
    lineas.append(f'<100>Recibo N: {pago.pk}')
    lineas.append(f'<100>Fecha: {pago.fecha_pago}')
    lineas.append(f'<100>Cliente: {cliente.nombre_completo}')
    lineas.append(f'<100>Prestamo #{pago.cuota.prestamo.pk}')
    lineas.append(f'<100>Cuota N: {pago.cuota.numero}')
    lineas.append(f'<100>Metodo: {pago.metodo or "-"}')
    lineas.append('<100>--------------------------------')
    lineas.append(f'<112>Total pagado: {pago.monto_pagado}')
    lineas.append('<101>Gracias por su pago!')

    return '\n'.join(lineas)


def generar_link_bluetooth_print(pago, es_copia):
    """Arma un enlace intent:// que abre la app 'Bluetooth Print' directo con
    el recibo ya armado, listo para imprimir en una impresora térmica Bluetooth
    ya emparejada. Si la app no está instalada, Chrome cae a la Play Store."""
    texto = _texto_ticket_bluetooth_print(pago, es_copia)
    extra_texto = quote(texto, safe='')
    fallback = quote('https://play.google.com/store/apps/details?id=mate.bluetoothprint', safe='')
    return (
        'intent://send/#Intent;'
        'action=android.intent.action.SEND;'
        'package=mate.bluetoothprint;'
        'type=text/plain;'
        f'S.android.intent.extra.TEXT={extra_texto};'
        f'S.browser_fallback_url={fallback};'
        'end'
    )
