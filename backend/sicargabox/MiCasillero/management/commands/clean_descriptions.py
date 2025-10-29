import re

from django.core.management.base import BaseCommand
from django.db import transaction

from MiCasillero.models import PartidaArancelaria


class Command(BaseCommand):
    help = "Limpia las descripciones de las partidas arancelarias eliminando guiones al inicio y después de pipes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula la limpieza sin hacer cambios reales",
        )

    def clean_description(self, description):
        # Función auxiliar para limpiar una vez
        def clean_once(text):
            # Limpiamos los guiones al inicio
            text = text.lstrip("-").strip()

            # Limpiamos los guiones después de cada pipe
            text = re.sub(r"\|\s*-+\s*", "| ", text)

            # Eliminamos espacios extras entre pipes
            text = re.sub(r"\s+\|\s+", " | ", text)

            # Eliminamos espacios múltiples
            return " ".join(text.split())

        # Aplicar la limpieza hasta que no haya más cambios
        prev_description = None
        current_description = description

        while prev_description != current_description:
            prev_description = current_description
            current_description = clean_once(current_description)

        return current_description

    def handle(self, *args, **options):
        # Obtener todas las partidas
        partidas = PartidaArancelaria.objects.all()
        total_partidas = partidas.count()

        # Mostrar algunas descripciones originales para debug
        self.stdout.write("\nMostrando algunas descripciones originales:")
        for partida in partidas.filter(descripcion__startswith="-")[:5]:
            self.stdout.write(f'[DEBUG] Descripción raw: "{partida.descripcion}"')

        # Contar partidas que necesitan limpieza
        partidas_a_limpiar = []
        for partida in partidas:
            descripcion_limpia = self.clean_description(partida.descripcion)
            if descripcion_limpia != partida.descripcion:
                partidas_a_limpiar.append((partida, descripcion_limpia))

        total_a_limpiar = len(partidas_a_limpiar)

        self.stdout.write(f"\nTotal de partidas: {total_partidas}")
        self.stdout.write(f"Partidas que necesitan limpieza: {total_a_limpiar}")

        if total_a_limpiar == 0:
            self.stdout.write(
                self.style.SUCCESS("No hay partidas que necesiten limpieza.")
            )
            return

        # Mostrar ejemplos
        self.stdout.write("\nEjemplos de partidas que serán limpiadas:")
        for partida, descripcion_limpia in partidas_a_limpiar[:5]:
            self.stdout.write(f"Antes: {partida.descripcion}")
            self.stdout.write(f"Después: {descripcion_limpia}")
            self.stdout.write("---")

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING("\nDRY RUN - No se realizarán cambios")
            )
            return

        # Confirmar antes de proceder
        confirm = input("\n¿Desea proceder con la limpieza? (s/n): ")
        if confirm.lower() != "s":
            self.stdout.write(self.style.WARNING("Operación cancelada"))
            return

        # Realizar la limpieza
        with transaction.atomic():
            for partida, descripcion_limpia in partidas_a_limpiar:
                partida.descripcion = descripcion_limpia
                partida.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nLimpieza completada. {total_a_limpiar} partidas actualizadas."
            )
        )
