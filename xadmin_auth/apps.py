from django.apps import AppConfig


class XadminAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'xadmin_auth'

    def ready(self):
        # from xadmin_db import signals  #noqa
        return True

