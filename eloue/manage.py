#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eloue.settings")

    try:
        from django.conf import settings
        #import settings  # Assumed to be in the same directory.
        os.environ['AWS_ACCESS_KEY_ID'] = settings.AWS_ACCESS_KEY_ID
        os.environ['AWS_SECRET_ACCESS_KEY'] = settings.AWS_SECRET_ACCESS_KEY
    except ImportError:
        sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
        sys.exit(1)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
