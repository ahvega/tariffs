from rest_framework import serializers

from MiCasillero.models import (Articulo, Cliente, Cotizacion,
                                PartidaArancelaria)


class PartidaArancelariaAPISerializer(serializers.ModelSerializer):
    """
    Serializer for Partida Arancelaria (Tariff Classification Item).

    Represents a tariff item with its associated tax rates, shipping category,
    and handling requirements for international courier services.

    Fields:
        id (int): Unique identifier
        item_no (str): Tariff item number (e.g., "4805.24.00.00")
        descripcion (str): Detailed description of the item
        partida_arancelaria (str): Tariff classification code
        impuesto_dai (decimal): DAI tax rate (0.00-1.00)
        impuesto_isc (decimal): ISC tax rate (0.00-1.00)
        impuesto_ispc (decimal): ISPC tax rate (0.00-1.00)
        impuesto_isv (decimal): ISV tax rate (0.00-1.00)
        courier_category (str): Shipping category (ALLOWED/RESTRICTED/PROHIBITED)
        restrictions (list): Array of shipping restrictions
        package_type (str): Required package type
        requires_special_handling (bool): Whether special handling is required
        special_instructions (str): Additional handling instructions
        max_weight_allowed (decimal): Maximum allowed weight (null if no limit)
        search_keywords (list): Keywords for search functionality
    """

    class Meta:
        model = PartidaArancelaria
        fields = [
            "id",
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
            "search_keywords",
        ]


class ClienteAPISerializer(serializers.ModelSerializer):
    """
    Serializer for Cliente (Customer).

    Represents a customer in the courier shipping system with their personal
    and contact information.

    Fields:
        id (int): Unique identifier
        codigo_cliente (str): Auto-generated customer code (read-only)
        nombres (str): First name(s)
        apellidos (str): Last name(s)
        telefono (str): Contact phone number
        correo_electronico (str): Email address
        nombre_corto (str): Auto-generated short name (read-only)
        direccion (str): Street address
        ciudad (str): City
        departamento (str): Department/State
        pais (str): Country
    """

    class Meta:
        model = Cliente
        fields = [
            "id",
            "codigo_cliente",
            "nombres",
            "apellidos",
            "telefono",
            "correo_electronico",
            "nombre_corto",
            "direccion",
            "ciudad",
            "departamento",
            "pais",
        ]
        read_only_fields = ["codigo_cliente", "nombre_corto"]


class CotizacionAPISerializer(serializers.ModelSerializer):
    """
    Serializer for Cotizacion (Shipping Quotation).

    Represents a shipping quotation that contains multiple articles
    for a specific customer.

    Fields:
        id (int): Unique identifier
        cliente (int): Customer ID (foreign key to Cliente)
        fecha_creacion (datetime): Creation timestamp (read-only, auto-generated)
        estado (str): Quotation status
    """

    class Meta:
        model = Cotizacion
        fields = ["id", "cliente", "fecha_creacion", "estado"]
        read_only_fields = ["fecha_creacion"]


class ArticuloAPISerializer(serializers.ModelSerializer):
    """
    Serializer for Articulo (Shipment Item).

    Represents an individual item within a quotation, including its physical
    dimensions, weight, value, and calculated tax information.

    Fields:
        id (int): Unique identifier
        cotizacion (int): Quotation ID (foreign key to Cotizacion)
        valor_articulo (decimal): Item value in local currency
        largo (decimal): Length in cm
        ancho (decimal): Width in cm
        alto (decimal): Height in cm
        peso (decimal): Actual weight in kg
        peso_volumetrico (decimal): Volumetric weight in kg (read-only, calculated)
        peso_a_usar (decimal): Weight to use for shipping calculation (read-only, max of peso and peso_volumetrico)
        partida_arancelaria (int): Tariff item ID (foreign key to PartidaArancelaria)
        impuesto_dai (decimal): DAI tax amount (read-only, auto-calculated)
        impuesto_isc (decimal): ISC tax amount (read-only, auto-calculated)
        impuesto_ispc (decimal): ISPC tax amount (read-only, auto-calculated)
        impuesto_isv (decimal): ISV tax amount (read-only, auto-calculated)
        impuesto_total (decimal): Total tax amount (read-only, auto-calculated)

    Note:
        All tax fields are automatically calculated upon creation based on the
        associated partida arancelaria's tax rates.
    """

    peso_volumetrico = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    peso_a_usar = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Articulo
        fields = [
            "id",
            "cotizacion",
            "valor_articulo",
            "largo",
            "ancho",
            "alto",
            "peso",
            "peso_volumetrico",
            "peso_a_usar",
            "partida_arancelaria",
            "impuesto_dai",
            "impuesto_isc",
            "impuesto_ispc",
            "impuesto_isv",
            "impuesto_total",
        ]
        read_only_fields = [
            "impuesto_dai",
            "impuesto_isc",
            "impuesto_ispc",
            "impuesto_isv",
            "impuesto_total",
        ]
