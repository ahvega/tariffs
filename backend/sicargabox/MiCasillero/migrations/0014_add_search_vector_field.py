# Generated manually to fix missing search_vector field

import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("MiCasillero", "0013_add_descripcion_original"),
    ]

    operations = [
        migrations.AddField(
            model_name="partidaarancelaria",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
    ]
