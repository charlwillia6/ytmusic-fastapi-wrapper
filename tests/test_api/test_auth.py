import pytest
from unittest.mock import patch
from fastapi import HTTPException
from app.schemas.models import CredentialsModel

@pytest.fixture
def mock_credentials():
    """Create mock credentials for testing"""
    return CredentialsModel(
        token="test_token",
        refresh_token="test_refresh_token",
        token_uri="test_token_uri",
        client_id="test_client_id",
        client_secret="test_client_secret",
        scopes=["https://www.googleapis.com/auth/youtube"]
    )

def test_login_no_code(test_client):
    """Test login endpoint without code parameter"""
    response = test_client.post("/api/v1/auth/login")
    assert response.status_code == 422

def test_login_success(test_client, mock_credentials):
    """Test successful login"""
    async def mock_get_oauth_creds(*args, **kwargs):
        return mock_credentials

    with patch("app.core.security.get_oauth_credentials", mock_get_oauth_creds):
        response = test_client.post("/api/v1/auth/login", params={"code": "valid_code"})
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "refresh_token" in data
        assert data["token"] == mock_credentials.token
        assert data["refresh_token"] == mock_credentials.refresh_token

def test_login_invalid_code(test_client):
    """Test login with invalid code"""
    async def mock_get_oauth_creds(*args, **kwargs):
        raise HTTPException(status_code=401)

    with patch("app.core.security.get_oauth_credentials", autospec=True) as mock_get_oauth_creds:
        mock_get_oauth_creds.side_effect = HTTPException(status_code=401)
        response = test_client.post("/api/v1/auth/login", params={"code": "invalid_code"})
        assert response.status_code == 401

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

def test_get_oauth_url(test_client):
    """Test get OAuth URL endpoint"""
    response = test_client.get("/api/v1/auth/oauth-url", headers={"User-Agent": "Test Client"})
    assert response.status_code == 200
    assert "url" in response.json()

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

def test_oauth_callback_success(test_client):
    """Test successful OAuth callback"""
    response = test_client.get(
        "/api/v1/auth/callback",
        params={"code": "test_code"},
        headers={"User-Agent": "Test Client"}
    )
    assert response.status_code == 200
    assert response.json()["token"] == "test_token"
    assert response.json()["refresh_token"] == "test_refresh_token"
    assert response.json()["client_id"] == "test_client_id"
