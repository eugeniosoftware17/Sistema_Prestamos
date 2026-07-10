from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import PagoForm
from .models import Cuota


class CuotaListView(ListView):
    model = Cuota
    template_name = 'pagos/index.html'
    context_object_name = 'cuotas'
    ordering = ['fecha_vencimiento']
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hoy'] = date.today()
        return context


def registrar_pago(request, pk):
    cuota = get_object_or_404(Cuota, pk=pk)

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.cuota = cuota
            pago.save()

            total_pagado = sum(p.monto_pagado for p in cuota.pagos.all())
            if total_pagado >= cuota.monto:
                cuota.estado = Cuota.Estado.PAGADA
                cuota.save()

            messages.success(request, 'Pago registrado correctamente.')
            return redirect('pagos:index')
    else:
        form = PagoForm(initial={'monto_pagado': cuota.monto, 'fecha_pago': date.today()})

    return render(request, 'pagos/registrar_pago.html', {'form': form, 'cuota': cuota})
