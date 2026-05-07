import os
import sys
from pathlib import Path


def main():
    root_dir = Path(__file__).resolve().parent
    django_dir = root_dir / "project"

    sys.path.insert(0, str(root_dir))
    sys.path.insert(0, str(django_dir))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
