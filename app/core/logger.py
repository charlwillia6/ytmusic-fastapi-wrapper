import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Log to stdout instead of file
    ]
)

logger = logging.getLogger(__name__)

def log_security_event(event_type: str, details: str) -> None:
    """Log security related events"""
    logger.info(f"Security event - {event_type}: {details}")
