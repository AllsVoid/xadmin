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
        from xadmin_db import signals as _xadmin_signals  #noqa
        
        # 注册退出处理器
        if bool(os.environ.get('XADMINSTART')):
            atexit.register(on_exit)
        
        # 不在启动时初始化缓存，避免警告
        # 缓存将在第一次访问时自动创建（通过信号）

