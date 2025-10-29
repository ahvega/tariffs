from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import auth_views, views

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
    # API Schema documentation
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
