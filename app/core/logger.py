
import logging
import sys
import json
from typing import Any

class JSONFormatter(logging.Formatter):
    """
    Formats logs as JSON objects for production observability.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record, self.datefmt)
        }
        
        # Inject custom attributes if they exist (e.g., document_id, stage)
        if hasattr(record, "extra_info"):
            log_obj.update(record.extra_info) # type: ignore
            
        # Include exception traceback if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)

def setup_logger(name: str = "TeacherAI") -> logging.Logger:
    """
    Initializes and returns a structured logger.
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate logs if setup is called multiple times
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)
    
    # Console handler for local development (Standard format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    console_handler.setFormatter(console_format)
    
    # File handler for production (JSON format)
    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(JSONFormatter())
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Singleton instance to be imported across the app
app_logger = setup_logger()