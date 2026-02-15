import logging
from pythonjsonlogger import jsonlogger
from app.core.config import settings


def setup_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    if settings.json_logs:
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    else:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(settings.log_level)


logger = logging.getLogger(__name__)
