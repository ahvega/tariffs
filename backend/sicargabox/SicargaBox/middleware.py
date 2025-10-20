from django.conf import settings
from django.utils import translation

LANGUAGE_SESSION_KEY = "django_language"


class AdminDefaultLanguageMiddleware:
    """Force Django admin to default to the project language when no preference is set."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_prefix = '/admin/'
        cookie_language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        session_language = None

        if hasattr(request, 'session'):
            session_language = request.session.get(LANGUAGE_SESSION_KEY)

        should_force_spanish = (
            request.path.startswith(admin_prefix)
            and not cookie_language
            and not session_language
        )

        if should_force_spanish:
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE

        response = self.get_response(request)

        if should_force_spanish:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, settings.LANGUAGE_CODE)
            translation.deactivate()

        return response
