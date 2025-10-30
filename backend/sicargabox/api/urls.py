from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import auth_views, shipping_views, views

router = DefaultRouter()
router.register(r"partidas-arancelarias", views.PartidaArancelariaViewSet)
router.register(r"clientes", views.ClienteViewSet)
router.register(r"cotizaciones", views.CotizacionViewSet)
router.register(r"articulos", views.ArticuloViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # Authentication endpoints
    path("auth/register/", auth_views.register, name="auth_register"),
    path("auth/login/", auth_views.login, name="auth_login"),
    path("auth/me/", auth_views.me, name="auth_me"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth_refresh"),
    # Shipping endpoints
    path("shipping/request/", shipping_views.create_shipping_request, name="shipping_request"),
    path("shipping/update/<int:envio_id>/", shipping_views.update_shipping_request, name="shipping_update"),
    path("shipping/list/", shipping_views.list_user_envios, name="shipping_list"),
    # System parameters
    path("parametros/publicos/", views.get_parametros_publicos, name="parametros_publicos"),
    # API Schema documentation
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
