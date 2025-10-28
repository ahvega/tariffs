from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from MiCasillero import views as views
from SicargaBox.views import htmx_home
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("MiCasillero/", include("MiCasillero.urls")),
    path("htmx/", htmx_home, name="htmx"),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("home/", views.home, name="home"),
    path("api/", include("api.urls")),
    # Public quote calculator at root level for easy access
    path("cotizador/", views.cotizador_view, name="cotizador_public"),
    path("cotizar/", views.cotizar, name="cotizar_public"),
    path("accept-quote/", views.accept_quote, name="accept_quote_public"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = (
        [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
        + urlpatterns
        + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
