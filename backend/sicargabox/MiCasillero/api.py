from rest_framework import viewsets, permissions

from . import serializers
from . import models


class AlertaViewSet(viewsets.ModelViewSet):
    """ViewSet for the Alerta class"""

    queryset = models.Alerta.objects.all()
    serializer_class = serializers.AlertaSerializer
    permission_classes = [permissions.IsAuthenticated]


class ArticuloViewSet(viewsets.ModelViewSet):
    """ViewSet for the Articulo class"""

    queryset = models.Articulo.objects.all()
    serializer_class = serializers.ArticuloSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClienteViewSet(viewsets.ModelViewSet):
    """ViewSet for the Cliente class"""

    queryset = models.Cliente.objects.all()
    serializer_class = serializers.ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]


class CotizacionViewSet(viewsets.ModelViewSet):
    """ViewSet for the Cotizacion class"""

    queryset = models.Cotizacion.objects.all()
    serializer_class = serializers.CotizacionSerializer
    permission_classes = [permissions.IsAuthenticated]


class EnvioViewSet(viewsets.ModelViewSet):
    """ViewSet for the Envio class"""

    queryset = models.Envio.objects.all()
    serializer_class = serializers.EnvioSerializer
    permission_classes = [permissions.IsAuthenticated]


class FacturaViewSet(viewsets.ModelViewSet):
    """ViewSet for the Factura class"""

    queryset = models.Factura.objects.all()
    serializer_class = serializers.FacturaSerializer
    permission_classes = [permissions.IsAuthenticated]


class ParametroSistemaViewSet(viewsets.ModelViewSet):
    """ViewSet for the ParametroSistema class"""

    queryset = models.ParametroSistema.objects.all()
    serializer_class = serializers.ParametroSistemaSerializer
    permission_classes = [permissions.IsAuthenticated]


class PartidaArancelariaViewSet(viewsets.ModelViewSet):
    """ViewSet for the PartidaArancelaria class"""

    queryset = models.PartidaArancelaria.objects.all()
    serializer_class = serializers.PartidaArancelariaSerializer
    permission_classes = [permissions.IsAuthenticated]
