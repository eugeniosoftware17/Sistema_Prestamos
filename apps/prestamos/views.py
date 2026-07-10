from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from pagos.services import generar_cuotas

from .forms import PrestamoForm
from .models import Prestamo


class PrestamoListView(ListView):
    model = Prestamo
    template_name = 'prestamos/index.html'
    context_object_name = 'prestamos'
    ordering = ['-fecha_inicio']
    paginate_by = 20


class PrestamoCreateView(CreateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'prestamos/form.html'
    success_url = reverse_lazy('prestamos:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        generar_cuotas(self.object)
        messages.success(self.request, 'Préstamo creado correctamente, cuotas generadas.')
        return response


class PrestamoUpdateView(UpdateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'prestamos/form.html'
    success_url = reverse_lazy('prestamos:index')

    def form_valid(self, form):
        messages.success(self.request, 'Préstamo actualizado correctamente.')
        return super().form_valid(form)


class PrestamoDeleteView(DeleteView):
    model = Prestamo
    template_name = 'prestamos/confirm_delete.html'
    success_url = reverse_lazy('prestamos:index')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, 'No se puede eliminar: el préstamo tiene cuotas con pagos registrados.')
            return redirect('prestamos:index')
        messages.success(self.request, 'Préstamo eliminado correctamente.')
        return response
