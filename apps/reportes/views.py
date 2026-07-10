from datetime import date

from django.db.models import Sum
from django.shortcuts import render

from pagos.models import Cuota, Pago
from prestamos.models import Prestamo


def index(request):
    hoy = date.today()

    prestamos_por_estado = []
    for valor, etiqueta in Prestamo.Estado.choices:
        queryset = Prestamo.objects.filter(estado=valor)
        prestamos_por_estado.append({
            'estado': etiqueta,
            'cantidad': queryset.count(),
            'monto': queryset.aggregate(total=Sum('monto'))['total'] or 0,
        })

    context = {
        'prestamos_por_estado': prestamos_por_estado,
        'cuotas_vencidas': Cuota.objects.filter(
            estado=Cuota.Estado.PENDIENTE, fecha_vencimiento__lt=hoy
        ).count(),
        'pagos_del_mes': Pago.objects.filter(
            fecha_pago__year=hoy.year, fecha_pago__month=hoy.month
        ).aggregate(total=Sum('monto_pagado'))['total'] or 0,
    }
    return render(request, 'reportes/index.html', context)
