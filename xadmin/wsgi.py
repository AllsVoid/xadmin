"""
WSGI config for xadmin project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
# from titw.utils import set_unique_id

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadmin.settings')
os.environ.setdefault('XADMINSTART', 'True')

application = get_wsgi_application()
