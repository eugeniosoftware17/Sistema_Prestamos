from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ConfiguracionSitio(TimeStampedModel):
    nombre = models.CharField(max_length=100, default='E2moneey')
    icono = models.ImageField(upload_to='configuracion/', blank=True, null=True)

    class Meta:
        verbose_name = 'Configuración del sitio'
        verbose_name_plural = 'Configuración del sitio'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.pk = 1
        if not self.created_at:
            existente = ConfiguracionSitio.objects.filter(pk=1).first()
            if existente:
                self.created_at = existente.created_at
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def cargar(cls):
        return cls.objects.get_or_create(pk=1)[0]
