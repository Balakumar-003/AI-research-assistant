import logging
import sys
import json
from datetime import datetime
from app.core.config import settings

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
            
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms
            
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging():
    logger = logging.getLogger("app")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
    # Remove existing handlers
    logger.handlers = []
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    logger.addHandler(handler)
    return logger

logger = setup_logging()
