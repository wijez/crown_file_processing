import logging


class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: "\033[1;34m%(asctime)s - %(levelname)s - %(message)s\033[0m",
        logging.INFO: "\033[1;32m%(asctime)s - %(levelname)s - %(message)s\033[0m",
        logging.WARNING: "\033[1;33m%(asctime)s - %(levelname)s - %(message)s\033[0m",
        logging.ERROR: "\033[1;31m%(asctime)s - %(levelname)s - %(message)s\033[0m",
        logging.CRITICAL: "\033[1;41m%(asctime)s - %(levelname)s - %(message)s\033[0m",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Config:
    @staticmethod
    def setup_logging(level=logging.DEBUG):
        # Tạo một logger
        logger = logging.getLogger(__name__)

        # Thiết lập formatter tùy chỉnh
        formatter = ColoredFormatter()
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Thiết lập mức độ logging
        logger.setLevel(level)
        return logger
