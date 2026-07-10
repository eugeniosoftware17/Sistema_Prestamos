from datetime import date

from django.db.models import Sum
from django.shortcuts import render

from clientes.models import Cliente
from pagos.models import Cuota
from prestamos.models import Prestamo


def home(request):
    context = {
        'total_clientes': Cliente.objects.count(),
        'prestamos_activos': Prestamo.objects.filter(estado=Prestamo.Estado.ACTIVO).count(),
        'cartera_activa': Prestamo.objects.filter(estado=Prestamo.Estado.ACTIVO).aggregate(
            total=Sum('monto')
        )['total'] or 0,
        'cuotas_vencidas': Cuota.objects.filter(
            estado=Cuota.Estado.PENDIENTE, fecha_vencimiento__lt=date.today()
        ).count(),
    }
    return render(request, 'core/home.html', context)


def ayuda(request):
    return render(request, 'core/ayuda.html')
