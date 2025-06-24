import logging
import os
from logging.handlers import RotatingFileHandler
from multiprocessing.util import get_logger
from typing import List, Tuple

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


class BufferedLogger:
    """
    A logger that buffers log messages in memory and flushes them.
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(name)
        self._buffer: List[Tuple[int, str]] = []

    def log(self, level: int, msg: str):
        self._buffer.append((level, msg))

    def info(self, msg: str):
        self.log(logging.INFO, msg)

    def debug(self, msg: str):
        self.log(logging.DEBUG, msg)

    def warning(self, msg: str):
        self.log(logging.WARNING, msg)

    def error(self, msg: str):
        self.log(logging.ERROR, msg)

    def flush(self):
        for level, msg in self._buffer:
            self.logger.log(level, msg)
        self._buffer.clear()
