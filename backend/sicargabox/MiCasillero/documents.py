from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import PartidaArancelaria


@registry.register_document
class PartidaArancelariaDocument(Document):
    # Campos específicos de Elasticsearch que queremos buscar
    item_no = fields.KeywordField()  # Usar Keyword para búsquedas exactas en códigos
    descripcion = fields.TextField(analyzer="spanish")  # Analizador para idioma español
    search_keywords = fields.KeywordField()  # Keywords para filtros o búsquedas
    # Campo combinado para búsqueda general difusa
    full_text_search = fields.TextField(analyzer="spanish")

    class Index:
        name = "partidas_arancelarias"  # Nombre del índice en Elasticsearch
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = PartidaArancelaria  # El modelo Django asociado
        fields = [  # Campos del modelo a incluir directamente
            "impuesto_dai",
            "impuesto_isc",
            "impuesto_ispc",
            "impuesto_isv",
            "courier_category",
        ]
        # Ignorar señales si no quieres actualizaciones automáticas al guardar/eliminar
        # ignore_signals = True
        # Opcional: Auto-refrescar índice después de cambios
        # auto_refresh = False

    def prepare_full_text_search(self, instance):
        # Prepara un campo combinado para búsqueda general
        keywords_str = (
            " ".join(instance.search_keywords) if instance.search_keywords else ""
        )
        return f"{instance.item_no} {instance.descripcion} {keywords_str}"

    def get_queryset(self):
        # Filtrar para indexar solo las partidas permitidas
        return super().get_queryset().filter(courier_category="ALLOWED")
