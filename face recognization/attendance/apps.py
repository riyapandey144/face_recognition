from django.apps import AppConfig
import sys


class AttendanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "attendance"

    def ready(self):
        """Warm up face encodings when Django app starts."""
        startup_commands = {"migrate", "makemigrations", "collectstatic", "shell", "createsuperuser", "check"}
        if any(command in sys.argv for command in startup_commands):
            return
        try:
            from .utils import load_known_faces

            load_known_faces(force_reload=True)
        except BaseException:
            # Keep app startup resilient if face libs are missing or DB is not ready.
            pass
