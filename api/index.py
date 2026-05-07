import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "face recognization"
DJANGO_DIR = APP_DIR / "project"

sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(DJANGO_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = get_wsgi_application()
application = app

if os.environ.get("VERCEL") and os.environ.get("DJANGO_AUTO_MIGRATE", "1") == "1":
    from django.core.management import call_command

    call_command("migrate", interactive=False, verbosity=0)
