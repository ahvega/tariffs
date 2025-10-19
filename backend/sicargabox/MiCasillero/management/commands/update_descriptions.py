from django.core.management.base import BaseCommand
from django.db import transaction
from MiCasillero.models import PartidaArancelaria
import pandas as pd
import os

class Command(BaseCommand):
    help = 'Actualiza las descripciones de las partidas arancelarias desde el archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la actualización sin hacer cambios reales',
        )
        parser.add_argument(
            '--csv-path',
            type=str,
            default='../../tools/pdf_parser/PartidasArancelariasHonduras2022.csv',
            help='Ruta al archivo CSV con las descripciones actualizadas',
        )

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        dry_run = options['dry_run']

        # Verificar que el archivo CSV existe
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'No se encontró el archivo CSV en: {csv_path}'))
            self.stdout.write(self.style.ERROR('Asegúrate de ejecutar el comando desde el directorio backend/sicargabox'))
            return

        # Leer el CSV
        try:
            df = pd.read_csv(csv_path)
            self.stdout.write(f'Archivo CSV leído correctamente. Total de registros: {len(df)}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al leer el archivo CSV: {str(e)}'))
            return

        # Crear diccionario de códigos y descripciones
        descriptions_dict = dict(zip(df['Codigo'], df['partida']))
        
        # Obtener todas las partidas que necesitan actualización
        partidas = PartidaArancelaria.objects.all()
        total_partidas = partidas.count()
        updated_count = 0
        skipped_count = 0
        error_count = 0

        self.stdout.write(f'Total de partidas en la base de datos: {total_partidas}')

        # Procesar cada partida
        for partida in partidas:
            try:
                if partida.item_no in descriptions_dict:
                    new_description = descriptions_dict[partida.item_no]
                    
                    # Verificar si la descripción es diferente
                    if partida.descripcion != new_description:
                        if dry_run:
                            self.stdout.write(f'\nSe actualizaría la descripción de la partida {partida.item_no}:')
                            self.stdout.write(f'Descripción actual: {partida.descripcion}')
                            self.stdout.write(f'Nueva descripción: {new_description}')
                        else:
                            with transaction.atomic():
                                partida.descripcion = new_description
                                partida.save()
                        updated_count += 1
                    else:
                        skipped_count += 1
                else:
                    self.stdout.write(self.style.WARNING(
                        f'No se encontró la partida {partida.item_no} en el CSV'
                    ))
                    error_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error al procesar la partida {partida.item_no}: {str(e)}'
                ))
                error_count += 1

        # Mostrar resumen
        self.stdout.write('\nResumen de la actualización:')
        self.stdout.write(f'Total de partidas procesadas: {total_partidas}')
        self.stdout.write(f'Partidas actualizadas: {updated_count}')
        self.stdout.write(f'Partidas sin cambios: {skipped_count}')
        self.stdout.write(f'Errores: {error_count}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No se realizaron cambios'))
        else:
            self.stdout.write(self.style.SUCCESS('\nActualización completada.')) 