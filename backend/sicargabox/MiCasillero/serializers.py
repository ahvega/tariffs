from rest_framework import serializers

from . import models


class AlertaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Alerta
        fields = [
            "envio",
            "cliente",
            "tipo_alerta",
            "mensaje",
            "fecha_envio",
            "estado",
        ]

class ArticuloSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Articulo
        fields = [
            "cotizacion",
            "valor_articulo",
            "largo",
            "ancho",
            "alto",
            "peso",
            "impuesto_dai",
            "impuesto_isc",
            "impuesto_ispc",
            "impuesto_isv",
            "impuesto_total",
        ]

class ClienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Cliente
        fields = [
            "nombres",
            "apellidos",
            "nombre_corto",
            "direccion",
            "telefono",
            "correo_electronico",
            "codigo_cliente",
            "fecha_registro",
        ]

class CotizacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Cotizacion
        fields = [
            "cliente",
            "fecha_creacion",
            "estado",
        ]

class EnvioSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Envio
        fields = [
            "cotizacion",
            "cliente",
            "tracking_number_original",
            "tracking_number_final",
            "direccion_casillero",
            "estado_envio",
            "flete",
            "fecha_actualizacion",
        ]

class FacturaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Factura
        fields = [
            "envio",
            "cliente",
            "flete",
            "total_impuesto_dai",
            "total_impuesto_isc",
            "total_impuesto_ispc",
            "total_impuesto_isv",
            "total_impuesto",
            "monto_total",
            "fecha_emision",
            "estado_pago",
        ]

class ParametroSistemaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ParametroSistema
        fields = [
            "nombre_parametro",
            "valor",
            "tipo_dato",
            "fecha_actualizacion",
        ]

class PartidaArancelariaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PartidaArancelaria
        fields = [
            "item_no",
            "descripcion",
            "partida_arancelaria",
            "impuesto_dai",
            "impuesto_isc",
            "impuesto_ispc",
            "impuesto_isv",
            "courier_category",
            "restrictions",
            "package_type",
            "requires_special_handling",
            "special_instructions",
            "max_weight_allowed",
            "search_keywords"
        ]
