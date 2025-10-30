from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from MiCasillero.models import Articulo, Cliente, Cotizacion, Envio, PartidaArancelaria


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


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (for authentication responses).

    Returns user information after successful login/registration.
    Used in authentication API responses and /api/auth/me/ endpoint.

    Fields:
        id (int): User ID
        username (str): Username
        email (str): Email address
        first_name (str): First name
        last_name (str): Last name
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles new user registration with password validation and confirmation.
    Automatically creates associated Cliente record upon successful registration.

    Fields:
        username (str): Unique username
        email (str): Email address (required)
        password (str): Password (write-only, validated)
        password2 (str): Password confirmation (write-only)
        first_name (str): First name (required)
        last_name (str): Last name (required)
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2", "first_name", "last_name"]

    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def validate_email(self, value):
        """Validate that email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        """Create user and associated Cliente record"""
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)

        # Assign user to UsuariosClientes group
        try:
            clientes_group = Group.objects.get(name="UsuariosClientes")
            user.groups.add(clientes_group)
        except Group.DoesNotExist:
            # Log warning but don't fail registration
            pass

        # Create associated Cliente record
        Cliente.objects.create(
            user=user,
            nombres=user.first_name,
            apellidos=user.last_name,
            correo_electronico=user.email,
        )

        return user


class ShippingRequestSerializer(serializers.Serializer):
    """
    Serializer for creating a shipping request (Envio).

    Accepts quote data and shipping information to create an Envio record.
    """
    # Quote reference
    quote_id = serializers.IntegerField(required=False, help_text="Cotizacion ID if already saved")

    # Quote data (if no quote_id provided)
    valor_articulo = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    peso = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    largo = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    ancho = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    alto = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    partida_arancelaria_id = serializers.IntegerField(required=False)
    descripcion_original = serializers.CharField(max_length=500, required=False)

    # Shipping information
    tracking_number_original = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="US tracking number (optional - can be added later)"
    )
    direccion_entrega = serializers.CharField(max_length=255, help_text="Delivery address")
    ciudad = serializers.CharField(max_length=100, required=False)
    departamento = serializers.CharField(max_length=100, required=False)
    instrucciones_especiales = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        """Validate that either quote_id or quote data is provided"""
        if not attrs.get('quote_id') and not all([
            attrs.get('valor_articulo'),
            attrs.get('peso'),
            attrs.get('partida_arancelaria_id'),
        ]):
            raise serializers.ValidationError(
                "Must provide either quote_id or complete quote data (valor_articulo, peso, partida_arancelaria_id)"
            )
        return attrs


class EnvioSerializer(serializers.ModelSerializer):
    """
    Serializer for Envio (Shipment).

    Returns shipment information including tracking numbers, status, and delivery details.
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre_corto', read_only=True)
    estado_envio_display = serializers.CharField(source='get_estado_envio_display', read_only=True)

    class Meta:
        model = Envio
        fields = [
            'id',
            'tracking_number_sicarga',
            'tracking_number_original',
            'estado_envio',
            'estado_envio_display',
            'cliente_nombre',
            'direccion_entrega',
            'instrucciones_especiales',
            'peso_estimado',
            'peso_real',
            'fecha_solicitud',
        ]
        read_only_fields = ['tracking_number_sicarga', 'fecha_solicitud']
