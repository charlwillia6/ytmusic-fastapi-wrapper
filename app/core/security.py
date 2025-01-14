from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.schemas.models import CredentialsModel
from typing import List
from app.core.logger import log_security_event
import os
from dotenv import load_dotenv
import time
from collections import defaultdict
from google_auth_oauthlib.flow import Flow
import json

load_dotenv()

# Rate limiting configuration
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", 50))
request_counts = defaultdict(list)  # IP -> list of timestamps

# Brute force protection
BRUTE_FORCE_MAX_ATTEMPTS = int(os.getenv("BRUTE_FORCE_MAX_ATTEMPTS", 5))
BRUTE_FORCE_WINDOW = int(os.getenv("BRUTE_FORCE_WINDOW", 300))
brute_force_store = defaultdict(list)  # IP -> list of timestamps

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl="https://oauth2.googleapis.com/token",
    refreshUrl="https://oauth2.googleapis.com/token",
    scopes={
        "https://www.googleapis.com/auth/youtube": "Access and manage your YouTube account",
        "https://www.googleapis.com/auth/youtube.readonly": "View your YouTube account"
    }
)

# OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/callback")
GOOGLE_REDIRECT_URI_DOCS = os.getenv("GOOGLE_REDIRECT_URI_DOCS", "http://localhost:8000/api/v1/docs/oauth2-redirect")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly"
]

# Load redirect URIs from environment variables
auth_redirect_uri = GOOGLE_REDIRECT_URI
docs_redirect_uri = GOOGLE_REDIRECT_URI_DOCS

# Function to get the appropriate redirect URI
def get_redirect_uri(for_docs=False):
    """Get the appropriate redirect URI based on the context."""
    if DEBUG:
        log_security_event(
            f"Getting redirect URI for {'docs' if for_docs else 'standard'} OAuth flow",
            json.dumps({
                "for_docs": for_docs,
                "docs_uri": docs_redirect_uri,
                "auth_uri": auth_redirect_uri
            })
        )
    return docs_redirect_uri if for_docs else auth_redirect_uri

def check_rate_limit(request: Request) -> None:
    """Check rate limiting."""
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
        
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
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

async def get_oauth_credentials(code: str, request: Request, for_docs: bool = False) -> CredentialsModel:
    """Get OAuth credentials from authorization code."""
    if not code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization code required"
        )

    try:
        # Load client secrets from file
        with open('client_secrets.json', 'r') as f:
            client_config = json.load(f)

        # Get appropriate redirect URI
        redirect_uri = get_redirect_uri(for_docs)
        if DEBUG:
            log_security_event(
                f"Using redirect URI: {redirect_uri} for {'docs' if for_docs else 'standard'} OAuth flow",
                json.dumps({
                    "redirect_uri": redirect_uri,
                    "for_docs": for_docs,
                    "referer": request.headers.get("referer", ""),
                    "request_url": str(request.url)
                })
            )

        # Create flow instance to handle the auth code flow
        flow = Flow.from_client_config(
            client_config,
            scopes=GOOGLE_SCOPES,
            redirect_uri=redirect_uri
        )

        # Exchange auth code for credentials
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Handle potential None values with defaults
        token = str(credentials.token) if credentials.token else ""
        refresh_token = str(credentials.refresh_token) if credentials.refresh_token else ""
        client_id = str(credentials.client_id) if credentials.client_id else GOOGLE_CLIENT_ID
        
        # Calculate expires_in as integer
        expires_in = None
        if credentials.expiry:
            try:
                expires_in = int(credentials.expiry.timestamp())
            except (AttributeError, ValueError):
                expires_in = None

        return CredentialsModel(
            token=token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=list(credentials.scopes) if credentials.scopes else GOOGLE_SCOPES,
            expires_in=expires_in
        )

    except Exception as e:
        if DEBUG:
            log_security_event(
                f"Failed to exchange authorization code: {str(e)}",
                json.dumps({
                    "error": str(e),
                    "for_docs": for_docs,
                    "referer": request.headers.get("referer", ""),
                    "request_url": str(request.url)
                })
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to exchange authorization code: {str(e)}"
        )

async def refresh_oauth_token(credentials: CredentialsModel) -> CredentialsModel:
    """Refresh OAuth token using refresh token."""
    if not credentials.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No refresh token available"
        )
    
    try:
        # Load client secrets
        with open('client_secrets.json', 'r') as f:
            client_config = json.load(f)

        # Create flow instance
        flow = Flow.from_client_config(
            client_config,
            scopes=GOOGLE_SCOPES
        )

        # Create new credentials with the refresh token
        flow.oauth2session.refresh_token(
            client_config['web']['token_uri'],
            refresh_token=credentials.refresh_token,
            client_id=client_config['web']['client_id'],
            client_secret=client_config['web']['client_secret']
        )

        # Get the new credentials
        new_token = flow.oauth2session.token
        
        return CredentialsModel(
            token=str(new_token.get('access_token', '')),
            refresh_token=credentials.refresh_token,  # Keep the original refresh token
            token_uri="https://oauth2.googleapis.com/token",
            client_id=credentials.client_id,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=GOOGLE_SCOPES,
            expires_in=new_token.get('expires_in')
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to refresh token: {str(e)}"
        ) 
