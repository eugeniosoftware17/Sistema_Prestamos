from datetime import date

from .models import ConfiguracionSitio


def configuracion_sitio(request):
    return {'config_sitio': ConfiguracionSitio.cargar()}


def notificaciones(request):
    if not request.user.is_authenticated:
        return {}

    from pagos.models import Cuota

    count = Cuota.objects.filter(
        estado=Cuota.Estado.PENDIENTE, fecha_vencimiento__lt=date.today()
    ).count()
    return {'notificaciones_vencidas': count}
