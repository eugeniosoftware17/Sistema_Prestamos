from django.test import TestCase

from .models import ConfiguracionSitio


class ConfiguracionSitioTests(TestCase):
    def test_cargar_crea_configuracion_por_defecto(self):
        config = ConfiguracionSitio.cargar()
        self.assertEqual(config.nombre, 'E2moneey')
        self.assertEqual(ConfiguracionSitio.objects.count(), 1)

    def test_cargar_siempre_devuelve_la_misma_instancia(self):
        primero = ConfiguracionSitio.cargar()
        primero.nombre = 'Otro Nombre'
        primero.save()

        segundo = ConfiguracionSitio.cargar()
        self.assertEqual(segundo.pk, 1)
        self.assertEqual(segundo.nombre, 'Otro Nombre')
        self.assertEqual(ConfiguracionSitio.objects.count(), 1)

    def test_no_se_puede_crear_una_segunda_fila(self):
        ConfiguracionSitio.cargar()
        otra = ConfiguracionSitio(nombre='Duplicado')
        otra.save()
        self.assertEqual(ConfiguracionSitio.objects.count(), 1)
        self.assertEqual(ConfiguracionSitio.objects.get().nombre, 'Duplicado')
