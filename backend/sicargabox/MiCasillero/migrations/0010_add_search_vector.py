from django.db import migrations
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class Migration(migrations.Migration):
    dependencies = [
        ('MiCasillero', '0009_clean_search_keywords'),
    ]

    operations = [
        # Index creation moved to migration 0015_add_search_vector_index
        # This migration is kept empty to maintain migration history
    ] 