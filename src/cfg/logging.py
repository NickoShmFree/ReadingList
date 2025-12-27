import os

LOG_DIR = "logs"
LOG_FILE = "app.log"
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"},
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, LOG_FILE),
            "maxBytes": 10_000_000,
            "backupCount": 5,
            "formatter": "default",
            "encoding": "utf-8",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {"level": "INFO", "handlers": ["file", "console"]},
    "loggers": {
        "uvicorn": {
            "level": "INFO",
            "handlers": ["file", "console"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["file", "console"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["file", "console"],
            "propagate": False,
        },
        "fastapi": {
            "level": "INFO",
            "handlers": ["file", "console"],
            "propagate": False,
        },
        "app": {  # для ваших кастомных логов
            "level": "INFO",
            "handlers": ["file", "console"],
            "propagate": False,
        },
    },
}
