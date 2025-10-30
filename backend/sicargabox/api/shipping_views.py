"""
Shipping Request API views.

Provides endpoint for creating shipping requests (Envio) from quotes.
"""

import uuid
from decimal import Decimal

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from MiCasillero.models import Articulo, Cliente, Cotizacion, Envio, PartidaArancelaria
from .serializers import EnvioSerializer, ShippingRequestSerializer


def generate_tracking_number():
    """Generate a unique internal tracking number"""
    return f"SC-{uuid.uuid4().hex[:10].upper()}"


@extend_schema(
    tags=["Shipping"],
    request=ShippingRequestSerializer,
    responses={201: EnvioSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_shipping_request(request):
    """
    Create a shipping request (Envio) from a quote.

    Requires authentication. Creates Cotizacion and Articulo records if not provided,
    then creates an Envio record with "Solicitado" status.

    Request body:
        - tracking_number_original (str): US tracking number
        - direccion_entrega (str): Delivery address
        - ciudad (str): City (optional)
        - departamento (str): Department/State (optional)
        - instrucciones_especiales (str): Special instructions (optional)
        - factura_compra (file): Purchase invoice (optional)
        - Either:
            - quote_id (int): Existing Cotizacion ID
            OR
            - valor_articulo (decimal): Item value
            - peso (decimal): Weight in lbs
            - largo (decimal): Length (optional)
            - ancho (decimal): Width (optional)
            - alto (decimal): Height (optional)
            - partida_arancelaria_id (int): Tariff item ID
            - descripcion_original (str): Item description (optional)

    Returns:
        - 201: Envio created successfully
        - 400: Validation error
        - 401: Not authenticated
    """
    serializer = ShippingRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        # Get or create Cliente for this user
        cliente, _ = Cliente.objects.get_or_create(
            user=request.user,
            defaults={
                "nombres": request.user.first_name,
                "apellidos": request.user.last_name,
                "correo_electronico": request.user.email,
            },
        )

        # Get or create Cotizacion
        if data.get("quote_id"):
            cotizacion = Cotizacion.objects.get(
                id=data["quote_id"], cliente=cliente
            )
        else:
            # Create new Cotizacion from quote data
            cotizacion = Cotizacion.objects.create(
                cliente=cliente, estado="aceptada"
            )

            # Create Articulo for this Cotizacion
            partida = PartidaArancelaria.objects.get(
                id=data["partida_arancelaria_id"]
            )

            Articulo.objects.create(
                cotizacion=cotizacion,
                valor_articulo=data["valor_articulo"],
                peso=data["peso"],
                largo=data.get("largo", Decimal("0.00")),
                ancho=data.get("ancho", Decimal("0.00")),
                alto=data.get("alto", Decimal("0.00")),
                partida_arancelaria=partida,
            )

        # Build complete address
        ciudad = data.get("ciudad", "")
        departamento = data.get("departamento", "")
        direccion_parts = [data["direccion_entrega"]]
        if ciudad:
            direccion_parts.append(ciudad)
        if departamento:
            direccion_parts.append(departamento)
        direccion_completa = ", ".join(direccion_parts)

        # Create Envio
        # Use peso from data directly (we just created the Articulo with this peso)
        peso_estimado = data.get("peso", Decimal("0.00"))

        # Determine initial status based on documentation completeness
        tracking_number = data.get("tracking_number_original", "")
        has_invoice = request.FILES.get("factura_compra") is not None

        # If both tracking and invoice are missing, set status to "Documentación Pendiente"
        # Otherwise, set to "Solicitado" (fully submitted)
        if not tracking_number and not has_invoice:
            initial_status = "Documentación Pendiente"
        else:
            initial_status = "Solicitado"

        envio = Envio.objects.create(
            cotizacion=cotizacion,
            cliente=cliente,
            tracking_number_original=tracking_number,
            tracking_number_sicarga=generate_tracking_number(),
            estado_envio=initial_status,
            peso_estimado=peso_estimado,
            direccion_entrega=direccion_completa,
            instrucciones_especiales=data.get("instrucciones_especiales", ""),
        )

        # Handle invoice upload if provided
        if has_invoice:
            envio.factura_compra = request.FILES["factura_compra"]
            envio.save()

        # TODO: Send confirmation email with tracking number
        # This will be implemented in a separate task

        # Return the created Envio
        response_serializer = EnvioSerializer(envio)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    except Cotizacion.DoesNotExist:
        return Response(
            {"error": "Cotización no encontrada"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except PartidaArancelaria.DoesNotExist:
        return Response(
            {"error": "Partida arancelaria no encontrada"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": f"Error al crear la solicitud de envío: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    tags=["Shipping"],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'tracking_number_original': {'type': 'string'},
                'factura_compra': {'type': 'string', 'format': 'binary'},
            }
        }
    },
    responses={200: EnvioSerializer},
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_shipping_request(request, envio_id):
    """
    Update a shipping request with missing documentation.

    Allows users to add tracking number and/or invoice to existing envíos.
    Automatically updates status from "Documentación Pendiente" to "Solicitado"
    when documentation is complete.

    URL Parameters:
        - envio_id (int): ID of the Envio to update

    Request body (multipart/form-data):
        - tracking_number_original (str): US tracking number (optional)
        - factura_compra (file): Purchase invoice (optional)

    Returns:
        - 200: Envio updated successfully
        - 403: Permission denied (not owner)
        - 404: Envio not found
        - 401: Not authenticated
    """
    try:
        # Get the envío
        envio = Envio.objects.get(id=envio_id)

        # Verify ownership (user must be the cliente associated with this envío)
        if envio.cliente.user != request.user:
            return Response(
                {"error": "No tienes permiso para actualizar este envío"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Track if any updates were made
        updated = False

        # Update tracking number if provided
        if 'tracking_number_original' in request.data:
            tracking_number = request.data['tracking_number_original'].strip()
            if tracking_number:
                envio.tracking_number_original = tracking_number
                updated = True

        # Update invoice if provided
        if request.FILES.get('factura_compra'):
            envio.factura_compra = request.FILES['factura_compra']
            updated = True

        # Auto-update status if documentation is now complete
        if envio.estado_envio == 'Documentación Pendiente':
            # Check if we now have both tracking and invoice
            has_tracking = bool(envio.tracking_number_original and envio.tracking_number_original.strip())
            has_invoice = bool(envio.factura_compra)

            # If we have either tracking or invoice, move to "Solicitado"
            if has_tracking or has_invoice:
                envio.estado_envio = 'Solicitado'
                updated = True

        if updated:
            envio.save()

        # Return updated envío
        serializer = EnvioSerializer(envio)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Envio.DoesNotExist:
        return Response(
            {"error": "Envío no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": f"Error al actualizar el envío: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    tags=["Shipping"],
    responses={200: EnvioSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_user_envios(request):
    """
    List all envíos for the authenticated user.

    Returns all shipping requests belonging to the current user,
    ordered by most recent first.

    Returns:
        - 200: List of user's envíos
        - 401: Not authenticated
    """
    try:
        # Get cliente for current user
        try:
            cliente = Cliente.objects.get(user=request.user)
        except Cliente.DoesNotExist:
            # User has no cliente record yet
            return Response([], status=status.HTTP_200_OK)

        # Get all envíos for this cliente
        envios = Envio.objects.filter(cliente=cliente).order_by('-fecha_solicitud')

        # Serialize and return
        serializer = EnvioSerializer(envios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": f"Error al obtener la lista de envíos: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
