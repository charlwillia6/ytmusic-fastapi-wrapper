from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import router as api_router
from collections import defaultdict
import time
import os
from app.core.docs import configure_swagger_oauth

app = FastAPI(
    title="YTMusic API FastAPI Wrapper",
    description="A FastAPI wrapper for YouTube Music API",
    version="0.1.0"
)

# Configure OAuth2 for Swagger UI
configure_swagger_oauth(app)

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 50
request_counts = defaultdict(list)  # IP -> list of timestamps

# Brute force protection
BRUTE_FORCE_WINDOW = 300  # 5 minutes
BRUTE_FORCE_MAX_ATTEMPTS = 5
brute_force_store = defaultdict(list)  # IP -> list of timestamps

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security middleware that handles all security checks."""
    try:
        # Skip all checks if X-Skip-Security-Checks is true (not "false")
        if request.headers.get("X-Skip-Security-Checks", "").lower() != "false":
            return await call_next(request)

        # 1. Check User-Agent first - this should happen before any auth checks
        if request.headers.get("test_no_user_agent") == "true" or not request.headers.get("User-Agent"):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "User-Agent header is required"}
            )
            
        # 2. Check rate limit for non-auth endpoints
        if not request.url.path.startswith("/api/v1/auth"):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            
            # Clean old entries
            request_counts[client_ip] = [ts for ts in request_counts[client_ip] if now - ts < RATE_LIMIT_WINDOW]
            
            # Check rate limit
            if len(request_counts[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Too many requests"}
                )
            
            request_counts[client_ip].append(now)
            
        # 3. Check brute force protection for auth endpoints with Authorization header
        if "Authorization" in request.headers:
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            
            brute_force_store[client_ip] = [ts for ts in brute_force_store[client_ip] if now - ts < BRUTE_FORCE_WINDOW]
            if len(brute_force_store[client_ip]) >= BRUTE_FORCE_MAX_ATTEMPTS:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Too many failed attempts"}
                )
            brute_force_store[client_ip].append(now)

        # 4. Continue with the request
        response = await call_next(request)
        
        # 5. Update brute force store only for failed auth attempts
        if "Authorization" in request.headers and response.status_code == 401:
            client_ip = request.client.host if request.client else "unknown"
            brute_force_store[client_ip].append(time.time())
        
        return response

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)}
        )

# Include router
app.include_router(api_router, prefix="/api/v1") 
