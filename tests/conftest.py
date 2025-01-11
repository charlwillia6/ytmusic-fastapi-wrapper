import pytest
from unittest.mock import patch, AsyncMock
from google.oauth2.credentials import Credentials
from app.schemas.models import CredentialsModel
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app
from app.db.session import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.models import Base, Credentials as DBCredentials, Session as DBSession
from datetime import datetime, timedelta, timezone
import uuid
from contextlib import ExitStack
import os

# Remove any existing patches
if hasattr(app, "dependency_overrides"):
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory database for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for testing
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_credentials():
    """Create test credentials."""
    return CredentialsModel(
        token="test_token",
        refresh_token="test_refresh_token",
        token_uri="https://oauth2.googleapis.com/token",
        client_id="test_client_id",
        client_secret="test_client_secret",
        scopes=["https://www.googleapis.com/auth/youtube"]
    )

@pytest.fixture
def test_google_creds(test_credentials):
    """Create Google OAuth2 credentials for testing"""
    return Credentials(
        token=test_credentials.token,
        refresh_token=test_credentials.refresh_token,
        token_uri=test_credentials.token_uri,
        client_id=test_credentials.client_id,
        client_secret=test_credentials.client_secret,
        scopes=test_credentials.scopes
    )

@pytest.fixture
def test_client(test_db):
    """Create a test client"""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.rollback()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def create_test_session(db, test_credentials):
    """Create a test session in the database"""
    db_credentials = DBCredentials(
        token=test_credentials.token,
        refresh_token=test_credentials.refresh_token,
        token_uri=test_credentials.token_uri,
        client_id=test_credentials.client_id,
        client_secret=test_credentials.client_secret,
        scopes=",".join(test_credentials.scopes)
    )
    db.add(db_credentials)
    db.flush()
    
    session_token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    db_session = DBSession(
        user_id=db_credentials.id,
        session_token=session_token,
        expires_at=expires_at,
        is_active=True
    )
    db.add(db_session)
    db.commit()
    
    return session_token

@pytest.fixture
def mock_auth_header(test_db, test_credentials):
    """Create mock auth header with valid session token"""
    session_token = create_test_session(test_db, test_credentials)
    return {"Authorization": f"Bearer {session_token}"}

@pytest.fixture
def authenticated_client(test_client, test_credentials, mock_auth_header, mock_security):
    """Create a test client with authentication."""
    client = TestClient(app)  # Create a new client instance
    
    def _authenticated_request(*args, **kwargs):
        # Add authorization header to all requests
        headers = kwargs.pop("headers", {})
        headers.update(mock_auth_header)
        headers.setdefault("User-Agent", "Test Client")
        
        # Skip security checks for non-security/auth tests
        url = str(kwargs.get("url", ""))
        if not any(path in url for path in ["/security", "/auth"]):
            headers["X-Skip-Security-Checks"] = "true"
        
        kwargs["headers"] = headers
        return client.request(*args, **kwargs)

    # Patch the client's request methods
    client.get = lambda *a, **kw: _authenticated_request("GET", *a, **kw)
    client.post = lambda *a, **kw: _authenticated_request("POST", *a, **kw)
    client.put = lambda *a, **kw: _authenticated_request("PUT", *a, **kw)
    client.delete = lambda *a, **kw: _authenticated_request("DELETE", *a, **kw)
    
    with mock_security:
        yield client

import json

@pytest.fixture
def mock_security(test_credentials):
    """Mock security-related functions"""
    async def mock_verify_token(token: str) -> dict:
        if token == "invalid_token":
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return {
            "sub": test_credentials.client_id,
            "scopes": test_credentials.scopes,
            "refresh_token": test_credentials.refresh_token,
            "client_secret": test_credentials.client_secret,
            "exp": 9999999999
        }
    
    async def mock_get_oauth_credentials(code: str, request=None) -> CredentialsModel:
        if code == "invalid_code":
            raise HTTPException(status_code=401, detail="Invalid authorization code")
        return test_credentials

    async def mock_get_current_user(token: str) -> CredentialsModel:
        if not token or token == "invalid_token":
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return test_credentials

    stack = ExitStack()
    # Security mocks
    stack.enter_context(patch("app.core.security.verify_token", AsyncMock(side_effect=mock_verify_token)))
    stack.enter_context(patch("app.core.security.get_current_user", AsyncMock(side_effect=mock_get_current_user)))
    return stack

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables."""
    with patch.dict(os.environ, {
        "GOOGLE_CLIENT_ID": "test_client_id",
        "GOOGLE_CLIENT_SECRET": "test_client_secret",
        "GOOGLE_REDIRECT_URI": "http://localhost:8000/api/v1/auth/callback",
        "DEBUG": "true"
    }):
        yield

@pytest.fixture
def security_test_client(test_db):
    """Create a test client specifically for security tests."""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.rollback()
    
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    
    def _request(*args, **kwargs):
        # Get or create headers
        headers = kwargs.pop("headers", {}).copy()  # Make a copy to avoid modifying the original
        
        # Always set X-Skip-Security-Checks to false for security tests unless explicitly set
        if "X-Skip-Security-Checks" not in headers:
            headers["X-Skip-Security-Checks"] = "false"
        
        # Handle User-Agent
        if headers.get("test_no_user_agent") == "true":
            headers.pop("User-Agent", None)  # Remove User-Agent if present
        elif "User-Agent" not in headers:
            headers["User-Agent"] = "Test Client"
        
        # Update kwargs with modified headers
        kwargs["headers"] = headers
        return client.request(*args, **kwargs)
    
    # Patch the client's request methods
    client.get = lambda *a, **kw: _request("GET", *a, **kw)
    client.post = lambda *a, **kw: _request("POST", *a, **kw)
    client.put = lambda *a, **kw: _request("PUT", *a, **kw)
    client.delete = lambda *a, **kw: _request("DELETE", *a, **kw)
    
    # Reset rate limit and brute force stores before each test
    from app.main import request_counts, brute_force_store
    request_counts.clear()
    brute_force_store.clear()
    
    return client
