# Generated manually to add search_vector index after field creation

from django.contrib.postgres.indexes import GinIndex
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("MiCasillero", "0014_add_search_vector_field"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="partidaarancelaria",
            index=GinIndex(fields=["search_vector"], name="partida_search_vector_idx"),
        ),
    ]
