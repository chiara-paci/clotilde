#!/usr/bin/env python3
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clotildecore.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    argv=sys.argv
    has_port=False
    for arg in argv:
        if arg.endswith("manage.py"): continue
        if arg=="runserver": continue
        if arg.startswith("-"): 
            continue
        has_port=True
        break
    if not has_port:
        argv.append("9000")

    execute_from_command_line(sys.argv)


