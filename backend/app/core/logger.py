import logging
import os
from logging.handlers import RotatingFileHandler
from multiprocessing.util import get_logger

logger = get_logger()


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Stream handler does console logging,
        # Check with 'docker logs your-container'
        stream_handler = logging.StreamHandler()
        stream_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

        # File logging with rotation
        os.makedirs("logs", exist_ok=True)
        file_handler = RotatingFileHandler(
            "logs/app.log", maxBytes=50 * 1024 * 1024, backupCount=9
        )
        file_handler.setFormatter(stream_formatter)
        logger.addHandler(file_handler)

    return logger
