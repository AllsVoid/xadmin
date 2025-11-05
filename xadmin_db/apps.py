import os
import atexit
from django.apps import AppConfig
from django.db.models import signals
from django.core.cache import cache
from loguru import logger


def on_exit():
    logger.info('django exiting...')
    cache.clear()
    logger.info('Bye!')


class XadminDBConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'xadmin_db'
    label = 'xadmin_db'

    def ready(self):
        from xadmin_db import models
        from xadmin_db import signals as _xadmin_signals  #noqa
        if not bool(os.environ.get('XADMINSTART')):
            return True
        
        signals.post_save.send(sender=models.SysDept, instance=None, created=False)
        signals.post_save.send(sender=models.SysMenu, instance=None, created=False)

        atexit.register(on_exit)

