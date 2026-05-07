import os
import sys

from django.core.asgi import get_asgi_application

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
application = get_asgi_application()
