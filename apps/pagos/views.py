from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from core.models import ConfiguracionSitio

from .forms import PagoForm
from .models import Cuota, Pago
from .services import enviar_recibo_por_correo, generar_link_bluetooth_print, generar_link_whatsapp


class CuotaListView(ListView):
    model = Cuota
    template_name = 'pagos/index.html'
    context_object_name = 'cuotas'
    ordering = ['fecha_vencimiento']
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        estado = self.request.GET.get('estado')
        if query:
            queryset = queryset.filter(prestamo__cliente__nombre_completo__icontains=query)
        if estado == 'vencida':
            queryset = queryset.filter(estado=Cuota.Estado.PENDIENTE, fecha_vencimiento__lt=date.today())
        elif estado == Cuota.Estado.PENDIENTE:
            queryset = queryset.filter(estado=Cuota.Estado.PENDIENTE, fecha_vencimiento__gte=date.today())
        elif estado:
            queryset = queryset.filter(estado=estado)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hoy'] = date.today()
        context['query'] = self.request.GET.get('q', '')
        context['estado'] = self.request.GET.get('estado', '')
        context['estados'] = Cuota.Estado.choices
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

            if enviar_recibo_por_correo(pago):
                messages.success(request, 'Pago registrado correctamente. Recibo enviado por correo.')
            else:
                messages.success(request, 'Pago registrado correctamente.')
            return redirect('pagos:index')
    else:
        form = PagoForm(initial={'monto_pagado': cuota.monto, 'fecha_pago': date.today()})

    return render(request, 'pagos/registrar_pago.html', {'form': form, 'cuota': cuota})


RECIBO_TEMPLATES = {
    ConfiguracionSitio.DisenoRecibo.FORMAL: 'pagos/recibo_formal.html',
    ConfiguracionSitio.DisenoRecibo.TICKET: 'pagos/recibo_ticket.html',
    ConfiguracionSitio.DisenoRecibo.MINIMALISTA: 'pagos/recibo_minimalista.html',
}


def recibo_pago(request, pk):
    pago = get_object_or_404(Pago, pk=pk)

    es_copia = pago.impreso
    if not pago.impreso:
        pago.impreso = True
        pago.save(update_fields=['impreso'])

    config = ConfiguracionSitio.cargar()
    template_name = RECIBO_TEMPLATES.get(config.diseno_recibo, 'pagos/recibo_formal.html')

    context = {
        'pago': pago,
        'es_copia': es_copia,
        'link_whatsapp': generar_link_whatsapp(pago),
        'link_bluetooth_print': generar_link_bluetooth_print(pago, es_copia),
    }
    return render(request, template_name, context)
