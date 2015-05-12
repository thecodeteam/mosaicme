#!/usr/bin/env python
import os
import sys
import dotenv


if __name__ == "__main__":

    try:
        dotenv.read_dotenv(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))
    except Exception as e:
        print(e)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
