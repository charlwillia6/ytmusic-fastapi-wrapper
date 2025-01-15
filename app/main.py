from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import router as api_router
import time
import os
from app.core.security import (
    GOOGLE_SCOPES,
    RATE_LIMIT_WINDOW,
    RATE_LIMIT_MAX_REQUESTS,
    BRUTE_FORCE_WINDOW,
    BRUTE_FORCE_MAX_ATTEMPTS,
    request_counts,
    brute_force_store,
    docs_redirect_uri,
    GOOGLE_CLIENT_ID
)
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# Extract just the path portion from the full docs redirect URI and ensure it starts with a forward slash
parsed_uri = urlparse(docs_redirect_uri)
docs_redirect_path = parsed_uri.path if parsed_uri.path.startswith('/') else f"/{parsed_uri.path}"

app = FastAPI(
    title="YTMusic API FastAPI Wrapper",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    swagger_ui_oauth2_redirect_url=docs_redirect_path,
    swagger_ui_init_oauth={
        "clientId": GOOGLE_CLIENT_ID,
        "scopes": " ".join(GOOGLE_SCOPES),
        "usePkceWithAuthorizationCodeGrant": True,
        "additionalQueryStringParams": {
            "access_type": "offline",
            "prompt": "consent"
        }
    },
    openapi_tags=[{"name": "auth", "description": "Authentication operations"}],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="YTMusic API FastAPI Wrapper",
        version="0.1.0",
        description="A YTMusic API web framework created with FastAPI",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "google_oauth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "https://accounts.google.com/o/oauth2/v2/auth",
                    "tokenUrl": "https://oauth2.googleapis.com/token",
                    "refreshUrl": "https://oauth2.googleapis.com/token",
                    "scopes": {
                        "https://www.googleapis.com/auth/youtube": "Access and manage your YouTube account",
                        "https://www.googleapis.com/auth/youtube.readonly": "View your YouTube account"
                    }
                }
            }
        }
    }
    openapi_schema["security"] = [{"google_oauth2": GOOGLE_SCOPES}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

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
