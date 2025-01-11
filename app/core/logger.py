import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create logger
logger = logging.getLogger("ytmusic-api")

# Add file handlers
file_handler = logging.FileHandler(log_dir / "app.log")
security_handler = logging.FileHandler(log_dir / "security.log")

file_handler.setLevel(logging.INFO)
security_handler.setLevel(logging.WARNING)

# Create formatters
standard_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
security_formatter = logging.Formatter(
    '%(asctime)s - SECURITY - %(levelname)s - %(message)s - %(extra)s'
)

file_handler.setFormatter(standard_formatter)
security_handler.setFormatter(security_formatter)

logger.addHandler(file_handler)
logger.addHandler(security_handler)

def log_security_event(
    event_type: str,
    message: str,
    level: str = "warning",
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """Log security events with additional context."""
    extra = extra or {}
    extra.update({
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    log_method = getattr(logger, level.lower(), logger.warning)
    log_method(message, extra={"extra": json.dumps(extra)})

# Example usage:
# log_security_event(
#     "auth_failure",
#     "Invalid token attempt",
#     "warning",
#     {"ip": "1.2.3.4", "token": "invalid_token"}
# )
