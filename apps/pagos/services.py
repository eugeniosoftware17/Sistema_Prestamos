import calendar
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

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
