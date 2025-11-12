# loguru_config.py

from loguru import logger
import sys
import logging
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"

# 创建日志目录（如果不存在）
LOG_DIR.mkdir(exist_ok=True)

logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="DEBUG")
logger.add(str(LOG_DIR / "xadmin.log"), rotation="50MB", retention=10, 
           compression="zip", level="DEBUG")

class InterceptHandler(logging.Handler):
    def emit(self, record):
        level = logger.level(record.levelname).name
        logger.log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0)
logging.getLogger("django").handlers = [InterceptHandler()]
