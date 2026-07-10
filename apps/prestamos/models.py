from django.db import models

from clientes.models import Cliente
from core.models import TimeStampedModel


class Prestamo(TimeStampedModel):
    class Estado(models.TextChoices):
        ACTIVO = 'activo', 'Activo'
        PAGADO = 'pagado', 'Pagado'
        VENCIDO = 'vencido', 'Vencido'
        CANCELADO = 'cancelado', 'Cancelado'

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='prestamos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    tasa_interes = models.DecimalField(max_digits=5, decimal_places=2, help_text='Porcentaje, ej: 5.00')
    plazo_meses = models.PositiveIntegerField()
    fecha_inicio = models.DateField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)

    def __str__(self):
        return f'Préstamo #{self.pk} - {self.cliente}'
