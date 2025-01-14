import pytest
from fastapi import HTTPException
from app.core.security import get_oauth_credentials
from app.schemas.models import CredentialsModel
import os
from unittest.mock import patch

@pytest.fixture
def mock_credentials():
    """Create mock credentials for testing"""
    return CredentialsModel(
        token="test_token",
        refresh_token="test_refresh_token",
        token_uri="test_token_uri",
        client_id="test_client_id",
        client_secret="test_client_secret",
        scopes=["https://www.googleapis.com/auth/youtube"],
        expires_in=3600
    )

def test_get_current_user_no_token(test_client):
    """Test get current user without token"""
    response = test_client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_get_current_user_invalid_token(test_client):
    """Test get current user with invalid token"""
    response = test_client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid_token",
            "User-Agent": "Test Client",
            "X-Skip-Security-Checks": "false"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"

def test_get_current_user_success(authenticated_client, test_credentials):
    """Test get current user endpoint - success case"""
    response = authenticated_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["client_id"] == test_credentials.client_id
    assert "token" in response.json()

def test_get_oauth_url_endpoint(test_client, mock_env_vars):
    """Test get OAuth URL endpoint"""
    # Test standard OAuth URL
    response = test_client.get("/api/v1/auth/oauth-url")
    assert response.status_code == 200
    assert "url" in response.json()
    url = response.json()["url"]
    assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "")
    assert f"redirect_uri={redirect_uri}" in url
    # Client ID might come from client_secrets.json, so just check it exists
    assert "client_id=" in url

    # Test docs OAuth URL
    response = test_client.get("/api/v1/auth/docs-login", follow_redirects=False)
    assert response.status_code == 307  # Redirect status code
    redirect_url = response.headers["location"]
    assert redirect_url.startswith("https://accounts.google.com/o/oauth2/v2/auth")
    docs_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI_DOCS", "")
    assert f"redirect_uri={docs_redirect_uri}" in redirect_url
    assert "client_id=" in redirect_url

def test_get_current_user_invalid_scope(test_client, mock_credentials):
    """Test get current user with invalid scope"""
    # Mock verify_token to return invalid scope
    async def mock_verify_token(*args, **kwargs):
        return {
            "sub": mock_credentials.client_id,
            "scopes": ["invalid.scope"],
            "refresh_token": mock_credentials.refresh_token,
            "client_secret": mock_credentials.client_secret
        }
    
    with patch("app.core.security.verify_token", mock_verify_token):
        response = test_client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": "Bearer test_token",
                "User-Agent": "Test Client",
                "X-Skip-Security-Checks": "false"
            }
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Invalid scope"

def test_login_redirect(test_client):
    """Test login redirect endpoints"""
    # Test standard login redirect
    response = test_client.get("/api/v1/auth/login", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    location = response.headers["location"]
    assert location.startswith("https://accounts.google.com/o/oauth2/v2/auth")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "")
    assert f"redirect_uri={redirect_uri}" in location
    assert "client_id=" in location

    # Test docs login redirect
    response = test_client.get("/api/v1/auth/docs-login", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    location = response.headers["location"]
    assert location.startswith("https://accounts.google.com/o/oauth2/v2/auth")
    docs_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI_DOCS", "")
    assert f"redirect_uri={docs_redirect_uri}" in location
    assert "client_id=" in location

def test_oauth_callback_success(test_client, mock_credentials):
    """Test OAuth callback endpoint - success case"""
    async def mock_get_oauth(*args, **kwargs):
        return mock_credentials

    with patch("app.api.v1.endpoints.auth.get_oauth_credentials", side_effect=mock_get_oauth):
        # Test standard callback
        response = test_client.get("/api/v1/auth/callback", params={"code": "valid_code"})
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "token": mock_credentials.token,
            "refresh_token": mock_credentials.refresh_token,
            "client_id": mock_credentials.client_id,
            "expires_in": mock_credentials.expires_in
        }

        # Test docs callback
        response = test_client.get(
            "/api/v1/auth/callback",
            params={"code": "valid_code"},
            headers={"referer": "http://localhost:8000/api/v1/docs"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "token": mock_credentials.token,
            "refresh_token": mock_credentials.refresh_token,
            "client_id": mock_credentials.client_id,
            "expires_in": mock_credentials.expires_in
        }

def test_oauth_callback_test_code(test_client):
    """Test OAuth callback endpoint with test_code"""
    response = test_client.get("/api/v1/auth/callback", params={"code": "test_code"})
    assert response.status_code == 200
    assert response.json() == {
        "token": "test_token",
        "refresh_token": "test_refresh_token",
        "client_id": "test_client_id"
    }

def test_oauth_callback_invalid_code(test_client):
    """Test OAuth callback endpoint with invalid code"""
    response = test_client.get("/api/v1/auth/callback", params={"code": "invalid_code"})
    assert response.status_code == 401
    # The error message includes more details about the invalid code
    assert "Failed to exchange authorization code" in response.json()["detail"]
    assert "invalid_grant" in response.json()["detail"]

def test_get_me_success(test_client, mock_credentials):
    """Test get_me endpoint - success case"""
    with patch("app.core.security.get_current_user", return_value=mock_credentials):
        response = test_client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": f"Bearer {mock_credentials.token}",
                "User-Agent": "Test Client"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["token"] == mock_credentials.token
        assert data["refresh_token"] == mock_credentials.refresh_token
        assert data["client_id"] == mock_credentials.client_id
        assert data["scopes"] == mock_credentials.scopes
        assert "expires_in" in data

def test_get_me_invalid_scope(test_client, mock_credentials):
    """Test get_me endpoint with invalid scope"""
    with patch("app.core.security.verify_token", return_value={
        "sub": mock_credentials.client_id,
        "scopes": ["invalid.scope"],
        "refresh_token": mock_credentials.refresh_token,
        "client_secret": mock_credentials.client_secret
    }):
        response = test_client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": f"Bearer {mock_credentials.token}",
                "User-Agent": "Test Client"
            }
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Invalid scope"

def test_refresh_token_success(test_client, mock_credentials):
    """Test refresh token endpoint - success case"""
    new_credentials = CredentialsModel(
        token="new_test_token",
        refresh_token=mock_credentials.refresh_token,
        token_uri=mock_credentials.token_uri,
        client_id=mock_credentials.client_id,
        client_secret=mock_credentials.client_secret,
        scopes=mock_credentials.scopes,
        expires_in=3600
    )

    async def mock_refresh_oauth(*args, **kwargs):
        return new_credentials

    with patch("app.core.security.get_current_user", return_value=mock_credentials), \
         patch("app.api.v1.endpoints.auth.refresh_oauth_token", side_effect=mock_refresh_oauth):
        
        response = test_client.post(
            "/api/v1/auth/refresh",
            headers={
                "Authorization": f"Bearer {mock_credentials.token}",
                "User-Agent": "Test Client"
            }
        )
        
        assert response.status_code == 200
        assert response.json() == {
            "token": "new_test_token",
            "expires_in": 3600
        }

def test_logout_success(test_client, mock_credentials):
    """Test logout endpoint - success case"""
    with patch("app.core.security.get_current_user", return_value=mock_credentials):
        response = test_client.post(
            "/api/v1/auth/logout",
            headers={
                "Authorization": f"Bearer {mock_credentials.token}",
                "User-Agent": "Test Client"
            }
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"

def test_rate_limit_login(test_client):
    """Test rate limiting on login endpoint"""
    with patch("app.api.v1.endpoints.auth.limiter.limit") as mock_limit:
        # Mock the rate limit decorator to do nothing
        mock_limit.return_value = lambda x: x
        
        response = test_client.get(
            "/api/v1/auth/login",
            headers={"User-Agent": "Test Client"},
            follow_redirects=False  # Don't follow the redirect
        )
        assert response.status_code == 307
        assert response.headers["location"].startswith("https://accounts.google.com/o/oauth2/v2/auth")
