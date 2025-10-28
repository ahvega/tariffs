from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

router = DefaultRouter()
router.register(r"partidas-arancelarias", views.PartidaArancelariaViewSet)
router.register(r"clientes", views.ClienteViewSet)
router.register(r"cotizaciones", views.CotizacionViewSet)
router.register(r"articulos", views.ArticuloViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # API Schema documentation
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
