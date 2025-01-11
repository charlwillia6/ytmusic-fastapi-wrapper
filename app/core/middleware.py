from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.logger import logger
from app.core.security import get_client_ip

limiter = Limiter(key_func=get_remote_address)

def rate_limit_callback(request: Request, response: RateLimitExceeded, key: str):
    """Callback for rate limit exceeded."""
    client_ip = get_client_ip(request)
    logger.warning(
        f"Rate limit exceeded for {client_ip} on {request.url.path}",
        extra={
            "ip": client_ip,
            "path": request.url.path,
            "key": key,
            "limit": response.limit
        }
    )
    return response

setattr(limiter, 'on_request_callback', rate_limit_callback)
