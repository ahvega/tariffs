from django.urls import path, include
from rest_framework import routers

from . import api
from . import views
from . import htmx

router = routers.DefaultRouter()
router.register("Alerta", api.AlertaViewSet)
router.register("Articulo", api.ArticuloViewSet)
router.register("Cliente", api.ClienteViewSet)
router.register("Cotizacion", api.CotizacionViewSet)
router.register("Envio", api.EnvioViewSet)
router.register("Factura", api.FacturaViewSet)
router.register("ParametroSistema", api.ParametroSistemaViewSet)
router.register("PartidaArancelaria", api.PartidaArancelariaViewSet)

urlpatterns = (
    path("api/v1/", include(router.urls)),
    path("Alerta/", views.AlertaListView.as_view(), name="MiCasillero_Alerta_list"),
    path("Alerta/create/", views.AlertaCreateView.as_view(), name="MiCasillero_Alerta_create"),
    path("Alerta/detail/<int:pk>/", views.AlertaDetailView.as_view(), name="MiCasillero_Alerta_detail"),
    path("Alerta/update/<int:pk>/", views.AlertaUpdateView.as_view(), name="MiCasillero_Alerta_update"),
    path("Alerta/delete/<int:pk>/", views.AlertaDeleteView.as_view(), name="MiCasillero_Alerta_delete"),
    path("Articulo/", views.ArticuloListView.as_view(), name="MiCasillero_Articulo_list"),
    path("Articulo/create/", views.ArticuloCreateView.as_view(), name="MiCasillero_Articulo_create"),
    path("Articulo/detail/<int:pk>/", views.ArticuloDetailView.as_view(), name="MiCasillero_Articulo_detail"),
    path("Articulo/update/<int:pk>/", views.ArticuloUpdateView.as_view(), name="MiCasillero_Articulo_update"),
    path("Articulo/delete/<int:pk>/", views.ArticuloDeleteView.as_view(), name="MiCasillero_Articulo_delete"),
    path("Cliente/", views.ClienteListView.as_view(), name="MiCasillero_Cliente_list"),
    path("Cliente/create/", views.ClienteCreateView.as_view(), name="MiCasillero_Cliente_create"),
    path("Cliente/detail/<int:pk>/", views.ClienteDetailView.as_view(), name="MiCasillero_Cliente_detail"),
    path("Cliente/update/<int:pk>/", views.ClienteUpdateView.as_view(), name="MiCasillero_Cliente_update"),
    path("Cliente/delete/<int:pk>/", views.ClienteDeleteView.as_view(), name="MiCasillero_Cliente_delete"),
    path("Cotizacion/", views.CotizacionListView.as_view(), name="MiCasillero_Cotizacion_list"),
    path("Cotizacion/create/", views.create_cotizacion, name="MiCasillero_Cotizacion_create"),
    path("Cotizacion/detail/<int:pk>/", views.CotizacionDetailView.as_view(), name="MiCasillero_Cotizacion_detail"),
    path("Cotizacion/update/<int:pk>/", views.CotizacionUpdateView.as_view(), name="MiCasillero_Cotizacion_update"),
    path("Cotizacion/delete/<int:pk>/", views.CotizacionDeleteView.as_view(), name="MiCasillero_Cotizacion_delete"),
    path("Cotizacion/add_articulo/<int:cotizacion_id>/", views.add_articulo, name="add_articulo"),
    path("Cotizacion/view_cotizacion/<int:cotizacion_id>/", views.view_cotizacion, name="view_cotizacion"),
    path("Envio/", views.EnvioListView.as_view(), name="MiCasillero_Envio_list"),
    path("Envio/create/", views.EnvioCreateView.as_view(), name="MiCasillero_Envio_create"),
    path("Envio/detail/<int:pk>/", views.EnvioDetailView.as_view(), name="MiCasillero_Envio_detail"),
    path("Envio/update/<int:pk>/", views.EnvioUpdateView.as_view(), name="MiCasillero_Envio_update"),
    path("Envio/delete/<int:pk>/", views.EnvioDeleteView.as_view(), name="MiCasillero_Envio_delete"),
    path("Factura/", views.FacturaListView.as_view(), name="MiCasillero_Factura_list"),
    path("Factura/create/", views.FacturaCreateView.as_view(), name="MiCasillero_Factura_create"),
    path("Factura/detail/<int:pk>/", views.FacturaDetailView.as_view(), name="MiCasillero_Factura_detail"),
    path("Factura/update/<int:pk>/", views.FacturaUpdateView.as_view(), name="MiCasillero_Factura_update"),
    path("Factura/delete/<int:pk>/", views.FacturaDeleteView.as_view(), name="MiCasillero_Factura_delete"),
    path("ParametroSistema/", views.ParametroSistemaListView.as_view(), name="MiCasillero_ParametroSistema_list"),
    path("ParametroSistema/create/", views.ParametroSistemaCreateView.as_view(),
         name="MiCasillero_ParametroSistema_create"),
    path("ParametroSistema/detail/<int:pk>/", views.ParametroSistemaDetailView.as_view(),
         name="MiCasillero_ParametroSistema_detail"),
    path("ParametroSistema/update/<int:pk>/", views.ParametroSistemaUpdateView.as_view(),
         name="MiCasillero_ParametroSistema_update"),
    path("ParametroSistema/delete/<int:pk>/", views.ParametroSistemaDeleteView.as_view(),
         name="MiCasillero_ParametroSistema_delete"),
    path("PartidaArancelaria/", views.PartidaArancelariaListView.as_view(), name="MiCasillero_PartidaArancelaria_list"),
    path("PartidaArancelaria/create/", views.PartidaArancelariaCreateView.as_view(),
         name="MiCasillero_PartidaArancelaria_create"),
    path("PartidaArancelaria/detail/<int:pk>/", views.PartidaArancelariaDetailView.as_view(),
         name="MiCasillero_PartidaArancelaria_detail"),
    path("PartidaArancelaria/update/<int:pk>/", views.PartidaArancelariaUpdateView.as_view(),
         name="MiCasillero_PartidaArancelaria_update"),
    path("PartidaArancelaria/delete/<int:pk>/", views.PartidaArancelariaDeleteView.as_view(),
         name="MiCasillero_PartidaArancelaria_delete"),


    path('partida_arancelaria_autocomplete/', views.partida_arancelaria_autocomplete,
         name='partida_arancelaria_autocomplete'),
    path('cotizador/', views.cotizador_view, name='cotizador'),
    path('cotizar/', views.cotizar, name='cotizar'),
    path('cotizar-json/', views.cotizar_json, name='cotizar_json'),
    path('buscar-partidas/', views.buscar_partidas, name='buscar_partidas'),
    path('accept-quote/', views.accept_quote, name='accept_quote'),

    path("htmx/Alerta/", htmx.HTMXAlertaListView.as_view(), name="MiCasillero_Alerta_htmx_list"),
    path("htmx/Alerta/create/", htmx.HTMXAlertaCreateView.as_view(), name="MiCasillero_Alerta_htmx_create"),
    path("htmx/Alerta/delete/<int:pk>/", htmx.HTMXAlertaDeleteView.as_view(), name="MiCasillero_Alerta_htmx_delete"),
    path("htmx/Articulo/", htmx.HTMXArticuloListView.as_view(), name="MiCasillero_Articulo_htmx_list"),
    path("htmx/Articulo/create/", htmx.HTMXArticuloCreateView.as_view(), name="MiCasillero_Articulo_htmx_create"),
    path("htmx/Articulo/delete/<int:pk>/", htmx.HTMXArticuloDeleteView.as_view(),
         name="MiCasillero_Articulo_htmx_delete"),
    path("htmx/Cliente/", htmx.HTMXClienteListView.as_view(), name="MiCasillero_Cliente_htmx_list"),
    path("htmx/Cliente/create/", htmx.HTMXClienteCreateView.as_view(), name="MiCasillero_Cliente_htmx_create"),
    path("htmx/Cliente/delete/<int:pk>/", htmx.HTMXClienteDeleteView.as_view(), name="MiCasillero_Cliente_htmx_delete"),
    path("htmx/Cotizacion/", htmx.HTMXCotizacionListView.as_view(), name="MiCasillero_Cotizacion_htmx_list"),
    path("htmx/Cotizacion/create/", htmx.HTMXCotizacionCreateView.as_view(), name="MiCasillero_Cotizacion_htmx_create"),
    path("htmx/Cotizacion/delete/<int:pk>/", htmx.HTMXCotizacionDeleteView.as_view(),
         name="MiCasillero_Cotizacion_htmx_delete"),
    path("htmx/Envio/", htmx.HTMXEnvioListView.as_view(), name="MiCasillero_Envio_htmx_list"),
    path("htmx/Envio/create/", htmx.HTMXEnvioCreateView.as_view(), name="MiCasillero_Envio_htmx_create"),
    path("htmx/Envio/delete/<int:pk>/", htmx.HTMXEnvioDeleteView.as_view(), name="MiCasillero_Envio_htmx_delete"),
    path("htmx/Factura/", htmx.HTMXFacturaListView.as_view(), name="MiCasillero_Factura_htmx_list"),
    path("htmx/Factura/create/", htmx.HTMXFacturaCreateView.as_view(), name="MiCasillero_Factura_htmx_create"),
    path("htmx/Factura/delete/<int:pk>/", htmx.HTMXFacturaDeleteView.as_view(), name="MiCasillero_Factura_htmx_delete"),
    path("htmx/ParametroSistema/", htmx.HTMXParametroSistemaListView.as_view(),
         name="MiCasillero_ParametroSistema_htmx_list"),
    path("htmx/ParametroSistema/create/", htmx.HTMXParametroSistemaCreateView.as_view(),
         name="MiCasillero_ParametroSistema_htmx_create"),
    path("htmx/ParametroSistema/delete/<int:pk>/", htmx.HTMXParametroSistemaDeleteView.as_view(),
         name="MiCasillero_ParametroSistema_htmx_delete"),
    path("htmx/PartidaArancelaria/", htmx.HTMXPartidaArancelariaListView.as_view(),
         name="MiCasillero_PartidaArancelaria_htmx_list"),
    path("htmx/PartidaArancelaria/create/", htmx.HTMXPartidaArancelariaCreateView.as_view(),
         name="MiCasillero_PartidaArancelaria_htmx_create"),
    path("htmx/PartidaArancelaria/delete/<int:pk>/", htmx.HTMXPartidaArancelariaDeleteView.as_view(),
         name="MiCasillero_PartidaArancelaria_htmx_delete"),
)
