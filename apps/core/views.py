from datetime import date

from django.db.models import Q, Sum
from django.shortcuts import render

from clientes.models import Cliente
from pagos.models import Cuota
from prestamos.models import Prestamo


def home(request):
    hoy = date.today()
    context = {
        'total_clientes': Cliente.objects.count(),
        'prestamos_activos': Prestamo.objects.filter(estado=Prestamo.Estado.ACTIVO).count(),
        'cartera_activa': Prestamo.objects.filter(estado=Prestamo.Estado.ACTIVO).aggregate(
            total=Sum('monto')
        )['total'] or 0,
        'cuotas_vencidas': Cuota.objects.filter(
            estado=Cuota.Estado.PENDIENTE, fecha_vencimiento__lt=hoy
        ).count(),
        'proximas_cuotas': Cuota.objects.filter(
            estado=Cuota.Estado.PENDIENTE
        ).select_related('prestamo__cliente').order_by('fecha_vencimiento')[:5],
        'hoy': hoy,
    }
    return render(request, 'core/home.html', context)


def ayuda(request):
    return render(request, 'core/ayuda.html')


def buscar(request):
    query = request.GET.get('q', '').strip()
    clientes = []
    prestamos = []

    if query:
        clientes = Cliente.objects.filter(
            Q(nombre_completo__icontains=query) | Q(cedula__icontains=query)
        )
        prestamos = Prestamo.objects.filter(
            cliente__nombre_completo__icontains=query
        ).select_related('cliente')

    context = {
        'query': query,
        'clientes': clientes,
        'prestamos': prestamos,
    }
    return render(request, 'core/buscar.html', context)
