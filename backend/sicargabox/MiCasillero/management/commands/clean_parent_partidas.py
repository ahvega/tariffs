from django.core.management.base import BaseCommand
from django.db import transaction
from MiCasillero.models import PartidaArancelaria
import logging
from django.db import models

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Elimina las partidas arancelarias que son padres de otras partidas, manteniendo solo las partidas de nivel 4'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué partidas se eliminarían sin realizar cambios',
        )
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Analiza la estructura de las partidas sin realizar cambios',
        )

    def handle(self, *args, **options):
        # Obtener todas las partidas
        all_partidas = PartidaArancelaria.objects.all()
        total_partidas = all_partidas.count()
        self.stdout.write(f'Total de partidas encontradas: {total_partidas}')

        if options['analyze']:
            # Analizar la estructura de las partidas
            self.stdout.write('\nAnálisis de estructura:')
            
            # Contar partidas con parent_category
            with_parent = PartidaArancelaria.objects.exclude(parent_category__isnull=True).count()
            self.stdout.write(f'Partidas con parent_category: {with_parent}')
            
            # Mostrar algunos ejemplos de partidas con parent_category
            self.stdout.write('\nEjemplos de partidas con parent_category:')
            for partida in PartidaArancelaria.objects.exclude(parent_category__isnull=True)[:5]:
                self.stdout.write(f'- {partida.item_no}: {partida.descripcion}')
                self.stdout.write(f'  Parent: {partida.parent_category.item_no if partida.parent_category else "None"}')
            
            # Mostrar distribución de courier_category
            self.stdout.write('\nDistribución de courier_category:')
            categories = PartidaArancelaria.objects.values('courier_category').annotate(count=models.Count('id'))
            for cat in categories:
                self.stdout.write(f'- {cat["courier_category"]}: {cat["count"]}')
            
            return

        # Identificar partidas padres
        parent_partidas = []
        for partida in all_partidas:
            # Si la partida es referenciada por otras partidas como padre
            if PartidaArancelaria.objects.filter(parent_category=partida).exists():
                parent_partidas.append(partida)

        parent_count = len(parent_partidas)
        self.stdout.write(f'Partidas padres encontradas: {parent_count}')

        if parent_count == 0:
            self.stdout.write(self.style.SUCCESS('No se encontraron partidas padres para eliminar.'))
            return

        # Mostrar detalles de las partidas que se eliminarán
        self.stdout.write('\nPartidas que serán eliminadas:')
        for partida in parent_partidas:
            self.stdout.write(f'- {partida.item_no}: {partida.descripcion}')
            # Mostrar las partidas hijas
            child_partidas = PartidaArancelaria.objects.filter(parent_category=partida)
            for child in child_partidas:
                self.stdout.write(f'  └─ {child.item_no}: {child.descripcion}')

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\nDRY RUN: No se realizarán cambios.'))
            return

        # Confirmar la eliminación
        confirm = input('\n¿Está seguro de que desea eliminar estas partidas? (s/N): ')
        if confirm.lower() != 's':
            self.stdout.write(self.style.WARNING('Operación cancelada.'))
            return

        # Eliminar las partidas padres
        try:
            with transaction.atomic():
                for partida in parent_partidas:
                    # Registrar antes de eliminar
                    logger.info(f'Eliminando partida padre: {partida.item_no} - {partida.descripcion}')
                    partida.delete()

            self.stdout.write(self.style.SUCCESS(
                f'\nSe eliminaron exitosamente {parent_count} partidas padres.'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'Quedan {PartidaArancelaria.objects.count()} partidas en la base de datos.'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al eliminar las partidas: {str(e)}'))
            raise 