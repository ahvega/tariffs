
from SicargaBox.settings import *  # noqa

# Override any settings required for tests here

# Disable Debug Toolbar for tests
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
}

# Remove debug_toolbar from middleware
MIDDLEWARE = [m for m in MIDDLEWARE if 'debug_toolbar' not in m]

# Remove debug_toolbar from installed apps
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']

# Speed up password hashing during tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use in-memory file storage for tests
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'