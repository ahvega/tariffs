from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from MiCasillero.models import Articulo, Cliente, Cotizacion, ParametroSistema, PartidaArancelaria

from .serializers import (
    ArticuloAPISerializer,
    ClienteAPISerializer,
    CotizacionAPISerializer,
    PartidaArancelariaAPISerializer,
)

# Create your views here.


@extend_schema(tags=["Partidas Arancelarias"])
class PartidaArancelariaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Partidas Arancelarias (Tariff Classification Items).

    Provides CRUD operations for tariff items used in international shipping.
    Each item includes:
    - Tariff codes and descriptions
    - Tax rates (DAI, ISC, ISPC, ISV)
    - Courier category (ALLOWED/RESTRICTED/PROHIBITED)
    - Shipping restrictions and special handling requirements

    **Available filters:**
    - item_no: Filter by tariff item number
    - partida_arancelaria: Filter by tariff classification code
    - courier_category: Filter by shipping category (ALLOWED/RESTRICTED/PROHIBITED)
    - package_type: Filter by package type
    - requires_special_handling: Filter items requiring special handling (true/false)

    **Search fields:**
    - descripcion: Search in item descriptions
    - item_no: Search by item number
    - partida_arancelaria: Search by tariff code
    - search_keywords: Search in generated keywords
    - special_instructions: Search in special instructions

    **Ordering:**
    - item_no: Order by item number
    - impuesto_dai: Order by DAI tax rate
    - courier_category: Order by courier category
    - requires_special_handling: Order by special handling requirement
    """

    queryset = PartidaArancelaria.objects.all()
    serializer_class = PartidaArancelariaAPISerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "item_no",
        "partida_arancelaria",
        "courier_category",
        "package_type",
        "requires_special_handling",
    ]
    search_fields = [
        "descripcion",
        "item_no",
        "partida_arancelaria",
        "search_keywords",
        "special_instructions",
    ]
    ordering_fields = [
        "item_no",
        "impuesto_dai",
        "courier_category",
        "requires_special_handling",
    ]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == "search_products":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="query",
                description="Search term for products",
                required=True,
                type=str,
            ),
        ],
        description="Search for tariff items by product description",
    )
    @action(detail=False, methods=["get"])
    def search_products(self, request):
        query = request.query_params.get("query", "")
        if not query:
            return Response({"error": "Query parameter is required"}, status=400)

        results = self.queryset.filter(descripcion__icontains=query)
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Clientes"])
class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Clientes (Customers).

    Handles customer information for the courier shipping system.
    Each customer record includes personal information, contact details,
    and location data.

    **Available filters:**
    - codigo_cliente: Filter by customer code

    **Search fields:**
    - nombres: Search by first name
    - apellidos: Search by last name
    - correo_electronico: Search by email
    - codigo_cliente: Search by customer code

    **Note:** Customer codes are auto-generated and read-only.
    """

    queryset = Cliente.objects.all()
    serializer_class = ClienteAPISerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["codigo_cliente"]
    search_fields = ["nombres", "apellidos", "correo_electronico", "codigo_cliente"]

    def perform_create(self, serializer):
        """
        Automatically associate the authenticated user with the new cliente.

        When creating a new cliente via the API, the user field is automatically
        set to the currently authenticated user making the request.
        """
        serializer.save(user=self.request.user)


@extend_schema(tags=["Cotizaciones"])
class CotizacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Cotizaciones (Shipping Quotations).

    Handles quotation creation and management for international shipments.
    Each quotation is associated with a customer and contains multiple articles.

    **Available filters:**
    - estado: Filter by quotation status
    - cliente: Filter by customer ID

    **Permissions:**
    - Staff users can view all quotations
    - Regular users can only view their own quotations

    **Note:** The fecha_creacion (creation date) field is auto-generated and read-only.
    """

    queryset = Cotizacion.objects.all()
    serializer_class = CotizacionAPISerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["estado", "cliente"]

    def get_queryset(self):
        """
        Filter quotations based on user permissions.

        Returns:
            QuerySet: All quotations for staff users, only user's own quotations for regular users
        """
        user = self.request.user
        if user.is_staff:
            return Cotizacion.objects.all()
        return Cotizacion.objects.filter(cliente__user=user)


@extend_schema(tags=["Articulos"])
class ArticuloViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Articulos (Shipment Items).

    Handles individual items within quotations, including their dimensions,
    weight, value, and associated tax calculations.

    **Available filters:**
    - cotizacion: Filter by quotation ID

    **Calculated fields:**
    - peso_volumetrico: Volumetric weight (calculated from dimensions)
    - peso_a_usar: Weight to use for shipping (max of actual weight and volumetric weight)
    - impuesto_dai, impuesto_isc, impuesto_ispc, impuesto_isv: Tax amounts
    - impuesto_total: Total tax amount

    **Note:** All tax-related fields are automatically calculated and are read-only.
    The calculation is based on the associated tariff item (partida_arancelaria).
    """

    queryset = Articulo.objects.all()
    serializer_class = ArticuloAPISerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["cotizacion"]

    def perform_create(self, serializer):
        """
        Calculate taxes when creating an article.

        The taxes are automatically calculated based on the article's value
        and the tax rates from its associated partida arancelaria.

        Args:
            serializer: The ArticuloSerializer instance with validated data
        """
        articulo = serializer.save()
        articulo.calcular_impuestos()
        articulo.save()


@extend_schema(
    tags=["System Parameters"],
    responses={200: dict},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_parametros_publicos(request):
    """
    Get public system parameters for frontend use.

    Returns system parameters needed by the frontend including:
    - direccion_consolidador: Miami warehouse address
    - direccion_oficina: Honduras office address for pickup
    - whatsapp_oficina: Office WhatsApp number
    - entrega_a_domicilio: Whether home delivery service is available

    Requires authentication.
    """
    try:
        parametros = {
            'direccion_consolidador': ParametroSistema.objects.get_valor('Dirección Consolidador'),
            'direccion_oficina': ParametroSistema.objects.get_valor('Dirección Oficina'),
            'whatsapp_oficina': ParametroSistema.objects.get_valor('WhatsApp Oficina'),
            'telefono_oficina': ParametroSistema.objects.get_valor('Teléfono Oficina'),
            'entrega_a_domicilio': ParametroSistema.objects.get_valor('Entrega a Domicilio'),
        }
        return Response({'success': True, 'data': parametros}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
