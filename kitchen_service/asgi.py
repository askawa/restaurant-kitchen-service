"""ASGI config for the Restaurant Kitchen Service project."""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kitchen_service.settings")

application = get_asgi_application()
