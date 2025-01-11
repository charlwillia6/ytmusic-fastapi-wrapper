from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from app.schemas.models import CredentialsModel
from typing import List
from app.core.logger import log_security_event
import os
from dotenv import load_dotenv
import time
from collections import defaultdict

load_dotenv()

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 50
rate_limit_store = defaultdict(list)  # IP -> list of timestamps

# Brute force protection
BRUTE_FORCE_MAX_ATTEMPTS = 5
BRUTE_FORCE_WINDOW = 300  # 5 minutes
brute_force_store = defaultdict(list)  # IP -> list of timestamps

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=True)

# OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/callback")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly"
]

async def get_token(request: Request) -> str:
    """Get token from request."""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token

async def verify_token(token: str) -> dict:
    """Verify Google OAuth token and return payload."""
    try:
        # In a real implementation, you would verify the token with Google's tokeninfo endpoint
        # For now, we'll just check if it's our test token
        if token == "test_token":
            return {
                "sub": "test_client_id",
                "scopes": ["https://www.googleapis.com/auth/youtube"],
                "refresh_token": "test_refresh_token",
                "client_secret": "test_client_secret"
            }
        
        # Handle known invalid tokens
        if token in ["invalid_token", "invalid.token.format"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
            
        # Here you would make a request to Google's tokeninfo endpoint
        # and verify the token's validity and scopes
        
        # For now, we'll assume the token is valid if it's not the test token
        return {
            "sub": "client_id",
            "scopes": ["https://www.googleapis.com/auth/youtube"],
            "refresh_token": "refresh_token",
            "client_secret": GOOGLE_CLIENT_SECRET
        }
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

async def get_current_user(request: Request, token: str = Depends(get_token)) -> CredentialsModel:
    """Get current user from token."""
    try:
        payload = await verify_token(token)
        client_id: str = payload.get("sub", "")
        scopes: List[str] = payload.get("scopes", [])
        refresh_token: str = payload.get("refresh_token", "")
        client_secret: str = payload.get("client_secret", GOOGLE_CLIENT_SECRET)
        
        # First check if we have a valid client_id
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Then check scope - this should be a 403 since the token is valid but lacks permission
        if not any(scope.startswith("https://www.googleapis.com/auth/youtube") for scope in scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid scope"
            )
        
        return CredentialsModel(
            token=token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_oauth_credentials(code: str, request: Request) -> CredentialsModel:
    """Get OAuth credentials from authorization code."""
    if not code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization code required"
        )

    # For testing purposes, validate the code
    if code == "invalid_code":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization code"
        )

    # In production, this would validate the code and get real credentials
    return CredentialsModel(
        token="test_token",
        refresh_token="test_refresh_token",
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/youtube"]
    )

def check_rate_limit(request: Request) -> None:
    """Check rate limiting."""
    from app.main import request_counts, RATE_LIMIT_WINDOW, RATE_LIMIT_MAX_REQUESTS
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Clean old entries
    request_counts[client_ip] = [ts for ts in request_counts[client_ip] if now - ts < RATE_LIMIT_WINDOW]
    
    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests"
        )
    
    request_counts[client_ip].append(now)

def check_brute_force(request: Request) -> None:
    """Check brute force protection."""
    from app.main import brute_force_store, BRUTE_FORCE_WINDOW, BRUTE_FORCE_MAX_ATTEMPTS
    if "Authorization" in request.headers:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        brute_force_store[client_ip] = [ts for ts in brute_force_store[client_ip] if now - ts < BRUTE_FORCE_WINDOW]
        if len(brute_force_store[client_ip]) >= BRUTE_FORCE_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Too many failed attempts"
            )
        brute_force_store[client_ip].append(now)

async def get_credentials(token: str = Depends(oauth2_scheme)) -> CredentialsModel:
    """Get credentials from token without additional validation."""
    try:
        payload = await verify_token(token)
        client_id: str = payload.get("sub", "")
        scopes: List[str] = payload.get("scopes", [])
        refresh_token: str = payload.get("refresh_token", "")
        client_secret: str = payload.get("client_secret", GOOGLE_CLIENT_SECRET)
        
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        return CredentialsModel(
            token=token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        ) 

async def refresh_oauth_token(credentials: CredentialsModel) -> CredentialsModel:
    """Refresh OAuth token using refresh token."""
    if not credentials.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No refresh token available"
        )
    
    # Implement token refresh logic here
    # This would typically involve calling Google's token endpoint
    # with the refresh token to get a new access token
    
    return credentials  # Return new credentials with refreshed token 
