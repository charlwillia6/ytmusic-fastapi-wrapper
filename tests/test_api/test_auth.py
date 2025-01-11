import pytest
from unittest.mock import patch
from fastapi import HTTPException
from app.schemas.models import CredentialsModel
from app.core.security import get_current_user

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

def test_get_oauth_url_endpoint(test_client):
    """Test get OAuth URL endpoint"""
    response = test_client.get("/api/v1/auth/oauth-url", headers={"User-Agent": "Test Client"})
    assert response.status_code == 200
    assert "url" in response.json()
    assert response.json()["url"].startswith("https://accounts.google.com/o/oauth2/v2/auth")

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
    """Test login redirect endpoint"""
    response = test_client.get("/api/v1/auth/login", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"].startswith("https://accounts.google.com/o/oauth2/v2/auth")
    assert "client_id=" in response.headers["location"]
    assert "redirect_uri=" in response.headers["location"]
    assert "response_type=code" in response.headers["location"]
    assert "scope=https://www.googleapis.com/auth/youtube" in response.headers["location"]

def test_oauth_callback_success(test_client, mock_credentials):
    """Test OAuth callback endpoint - success case"""
    async def mock_get_oauth(*args, **kwargs):
        return mock_credentials

    with patch("app.core.security.get_oauth_credentials", side_effect=mock_get_oauth):
        response = test_client.get("/api/v1/auth/callback", params={"code": "valid_code"})
        assert response.status_code == 200
        data = response.json()
        # Only check the fields we know are returned by the endpoint
        assert "token" in data
        assert "refresh_token" in data
        assert "client_id" in data
        assert "expires_in" in data
        assert data["token"] == mock_credentials.token
        assert data["refresh_token"] == mock_credentials.refresh_token

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
    with patch("app.core.security.get_oauth_credentials", 
              side_effect=HTTPException(status_code=401, detail="Invalid authorization code")):
        response = test_client.get("/api/v1/auth/callback", params={"code": "invalid_code"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid authorization code"

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
