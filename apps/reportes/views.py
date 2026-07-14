from datetime import date

from django.db.models import Avg, Sum
from django.shortcuts import render

from pagos.models import Cuota, Pago
from prestamos.models import Prestamo

MESES_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']


def index(request):
    hoy = date.today()

    prestamos_por_estado = []
    for valor, etiqueta in Prestamo.Estado.choices:
        queryset = Prestamo.objects.filter(estado=valor)
        prestamos_por_estado.append({
            'valor': valor,
            'estado': etiqueta,
            'cantidad': queryset.count(),
            'monto': queryset.aggregate(total=Sum('monto'))['total'] or 0,
        })
    max_cantidad = max((fila['cantidad'] for fila in prestamos_por_estado), default=0) or 1

    cuotas_vencidas = Cuota.objects.filter(estado=Cuota.Estado.PENDIENTE, fecha_vencimiento__lt=hoy).count()
    cuotas_pendientes = Cuota.objects.filter(
        estado=Cuota.Estado.PENDIENTE, fecha_vencimiento__gte=hoy
    ).count()
    cuotas_pagadas = Cuota.objects.filter(estado=Cuota.Estado.PAGADA).count()
    total_cuotas = cuotas_vencidas + cuotas_pendientes + cuotas_pagadas
    tasa_morosidad = round(cuotas_vencidas / total_cuotas * 100, 1) if total_cuotas else 0

    cobros_por_mes = []
    for i in range(5, -1, -1):
        mes_index = hoy.month - 1 - i
        anio = hoy.year + mes_index // 12
        mes = mes_index % 12 + 1
        total = Pago.objects.filter(fecha_pago__year=anio, fecha_pago__month=mes).aggregate(
            total=Sum('monto_pagado')
        )['total'] or 0
        cobros_por_mes.append({'mes': f'{MESES_ES[mes - 1]} {anio}', 'total': total})
    max_cobro = max((fila['total'] for fila in cobros_por_mes), default=0) or 1

    context = {
        'prestamos_por_estado': prestamos_por_estado,
        'max_cantidad': max_cantidad,
        'cuotas_vencidas': cuotas_vencidas,
        'cuotas_pendientes': cuotas_pendientes,
        'cuotas_pagadas': cuotas_pagadas,
        'tasa_morosidad': tasa_morosidad,
        'pagos_del_mes': Pago.objects.filter(
            fecha_pago__year=hoy.year, fecha_pago__month=hoy.month
        ).aggregate(total=Sum('monto_pagado'))['total'] or 0,
        'promedio_prestamo': round(Prestamo.objects.aggregate(avg=Avg('monto'))['avg'] or 0, 2),
        'cartera_total': Prestamo.objects.aggregate(total=Sum('monto'))['total'] or 0,
        'cobros_por_mes': cobros_por_mes,
        'max_cobro': max_cobro,
    }
    return render(request, 'reportes/index.html', context)
