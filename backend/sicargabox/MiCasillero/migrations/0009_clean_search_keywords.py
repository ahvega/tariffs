from django.db import migrations
import json

def clean_search_keywords(apps, schema_editor):
    PartidaArancelaria = apps.get_model('MiCasillero', 'PartidaArancelaria')
    db_alias = schema_editor.connection.alias
    
    # Primero, convertir el campo a texto temporal
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE "MiCasillero_partidaarancelaria" 
            ALTER COLUMN search_keywords TYPE text 
            USING search_keywords::text
        """)
    
    # Luego, actualizar cada registro con una lista vacía en formato JSON
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            UPDATE "MiCasillero_partidaarancelaria" 
            SET search_keywords = '[]'
        """)
    
    # Finalmente, convertir el campo a JSONB
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE "MiCasillero_partidaarancelaria" 
            ALTER COLUMN search_keywords TYPE jsonb 
            USING search_keywords::jsonb
        """)

def reverse_clean_search_keywords(apps, schema_editor):
    # Si necesitamos revertir, convertimos de vuelta a texto
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE "MiCasillero_partidaarancelaria" 
            ALTER COLUMN search_keywords TYPE text
        """)

class Migration(migrations.Migration):
    dependencies = [
        ('MiCasillero', '0008_remove_partidaarancelaria_fecha_actualizacion_and_more'),
    ]

    operations = [
        migrations.RunPython(
            clean_search_keywords,
            reverse_code=reverse_clean_search_keywords
        ),
    ] 