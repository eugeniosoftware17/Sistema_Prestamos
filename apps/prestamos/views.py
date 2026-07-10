from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

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
        messages.success(self.request, 'Préstamo creado correctamente.')
        return super().form_valid(form)


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
        messages.success(self.request, 'Préstamo eliminado correctamente.')
        return super().form_valid(form)
