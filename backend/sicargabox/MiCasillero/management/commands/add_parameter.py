from django.core.management.base import BaseCommand
from MiCasillero.models import ParametroSistema


class Command(BaseCommand):
    help = 'Agregar parámetros al modelo ParametroSistema'

    def handle(self, *args, **kwargs):
        parametros = [
            {
                'nombre_parametro': 'Prefijo del Código de Cliente',
                'tipo_dato': 'STRING',
                'valor': '000015'
            },
            {
                'nombre_parametro': 'Permitir Consolidación de Paquetes',
                'tipo_dato': 'BOOLEAN',
                'valor': 'false'
            },

            {
                'nombre_parametro': 'Costo Flete por Libra en USD$',
                'tipo_dato': 'FLOAT',
                'valor': '2.5'
            }
        ]

        for parametro in parametros:
            obj, created = ParametroSistema.objects.update_or_create(
                nombre_parametro=parametro['nombre_parametro'],
                defaults={'tipo_dato': parametro['tipo_dato'], 'valor': parametro['valor']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Parámetro "{parametro["nombre_parametro"]}" creado.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Parámetro "{parametro["nombre_parametro"]}" actualizado.'))
