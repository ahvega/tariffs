# SicargaBox/MiCasillero/formats.py

from django.conf.locale.es import formats as es_formats

# Formato de números
es_formats.NUMBER_GROUPING = 3
es_formats.DECIMAL_SEPARATOR = "."
es_formats.THOUSAND_SEPARATOR = ","

# Formato de fechas
es_formats.DATE_FORMAT = "d/m/Y"
es_formats.DATETIME_FORMAT = "d/m/Y H:i:s"
es_formats.TIME_FORMAT = "H:i:s"
