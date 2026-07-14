from django.db import models

from core.models import TimeStampedModel
from prestamos.models import Prestamo


class Cuota(TimeStampedModel):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        PAGADA = 'pagada', 'Pagada'
        VENCIDA = 'vencida', 'Vencida'

    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='cuotas')
    numero = models.PositiveIntegerField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)

    class Meta:
        unique_together = ('prestamo', 'numero')
        ordering = ['numero']

    def __str__(self):
        return f'Cuota {self.numero} - Préstamo #{self.prestamo_id}'


class Pago(TimeStampedModel):
    cuota = models.ForeignKey(Cuota, on_delete=models.PROTECT, related_name='pagos')
    monto_pagado = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateField()
    metodo = models.CharField(max_length=50, blank=True)
    impreso = models.BooleanField(default=False)

    def __str__(self):
        return f'Pago de {self.monto_pagado} - {self.cuota}'
