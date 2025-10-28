from django.core.management.base import BaseCommand
from MiCasillero.models import PartidaArancelaria


class Command(BaseCommand):
    help = "Clear all existing Partidas Arancelarias data"

    def handle(self, *args, **options):
        count = PartidaArancelaria.objects.count()
        PartidaArancelaria.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"Successfully deleted {count} Partidas Arancelarias")
        )
