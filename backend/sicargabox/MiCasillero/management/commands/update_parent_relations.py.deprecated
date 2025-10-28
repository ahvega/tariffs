from django.core.management.base import BaseCommand
from django.db import transaction
from MiCasillero.models import PartidaArancelaria
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Actualiza las relaciones padre-hijo de las partidas arancelarias usando el CSV original'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Ruta al archivo CSV original con la estructura jerárquica'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué relaciones se actualizarían sin realizar cambios',
        )

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        self.stdout.write(f'Leyendo archivo CSV: {csv_path}')
        
        try:
            # Leer el CSV
            df = pd.read_csv(csv_path, encoding='utf-8', sep=',')
            self.stdout.write(f'Total de registros en CSV: {len(df)}')
            
            # Crear un diccionario de códigos a IDs de la base de datos
            partidas_dict = {
                partida.item_no: partida.id 
                for partida in PartidaArancelaria.objects.all()
            }
            
            # Contadores para estadísticas
            total_relations = 0
            updated_relations = 0
            skipped_relations = 0
            errors = 0
            
            # Lista para almacenar las actualizaciones
            updates = []
            
            # Procesar cada fila del CSV
            for _, row in df.iterrows():
                codigo = str(row['Codigo']).strip()
                padre = str(row['padre']).strip() if pd.notna(row['padre']) else None
                
                if codigo in partidas_dict and padre and padre in partidas_dict:
                    total_relations += 1
                    updates.append({
                        'id': partidas_dict[codigo],
                        'parent_id': partidas_dict[padre]
                    })
                elif codigo in partidas_dict:
                    skipped_relations += 1
                else:
                    errors += 1
                    self.stdout.write(
                        self.style.WARNING(f'Código no encontrado en la base de datos: {codigo}')
                    )
            
            # Mostrar resumen
            self.stdout.write('\nResumen de relaciones encontradas:')
            self.stdout.write(f'Total de relaciones en CSV: {total_relations}')
            self.stdout.write(f'Relaciones omitidas (sin padre): {skipped_relations}')
            self.stdout.write(f'Errores (códigos no encontrados): {errors}')
            
            if options['dry_run']:
                self.stdout.write(self.style.WARNING('\nDRY RUN: No se realizarán cambios.'))
                if updates:
                    self.stdout.write('\nEjemplos de relaciones que se actualizarían:')
                    for update in updates[:5]:
                        partida = PartidaArancelaria.objects.get(id=update['id'])
                        parent = PartidaArancelaria.objects.get(id=update['parent_id'])
                        self.stdout.write(f'- {partida.item_no} -> {parent.item_no}')
                return
            
            # Confirmar la actualización
            if updates:
                confirm = input('\n¿Está seguro de que desea actualizar las relaciones? (s/N): ')
                if confirm.lower() != 's':
                    self.stdout.write(self.style.WARNING('Operación cancelada.'))
                    return
                
                # Realizar las actualizaciones
                with transaction.atomic():
                    for update in updates:
                        try:
                            partida = PartidaArancelaria.objects.get(id=update['id'])
                            partida.parent_category_id = update['parent_id']
                            partida.save()
                            updated_relations += 1
                        except Exception as e:
                            errors += 1
                            logger.error(f'Error actualizando partida {update["id"]}: {str(e)}')
                
                self.stdout.write(self.style.SUCCESS(
                    f'\nSe actualizaron exitosamente {updated_relations} relaciones.'
                ))
                if errors > 0:
                    self.stdout.write(self.style.WARNING(
                        f'Se encontraron {errors} errores durante la actualización.'
                    ))
            else:
                self.stdout.write(self.style.WARNING('No hay relaciones para actualizar.'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error procesando el archivo: {str(e)}'))
            raise 