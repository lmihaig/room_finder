# src/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
from . import config


def setup_logging():
    """
    Configures the root logger to write to a rotating file and the console.
    """
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the lowest level of messages to handle

    # Create a formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # --- Console Handler ---
    # This handler prints logs to your terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- Rotating File Handler ---
    # This handler writes logs to a file, with rotation to control size.
    file_handler = RotatingFileHandler(
        config.LOG_FILE_PATH,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logging.info("Logging configured successfully.")
