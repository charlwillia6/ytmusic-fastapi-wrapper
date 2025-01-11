from unittest.mock import patch
from datetime import datetime, timedelta
from app.core.security import get_oauth_credentials

def test_rate_limit(security_test_client):
    """Test rate limiting middleware"""
    # Make multiple requests in quick succession
    for _ in range(101):  # Our rate limit is 100 requests per minute
        security_test_client.get(
            "/api/v1/search",
            headers={
                "User-Agent": "Test Client",
                "X-Skip-Security-Checks": "false"
            }
        )
    
    # Next request should be rate limited
    response = security_test_client.get(
        "/api/v1/search",
        headers={
            "User-Agent": "Test Client",
            "X-Skip-Security-Checks": "false"
        }
    )
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]

def test_invalid_token_format(security_test_client):
    """Test invalid token format handling."""
    response = security_test_client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid.token.format",
            "User-Agent": "Test Client",
            "X-Skip-Security-Checks": "false"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"

def test_missing_user_agent(security_test_client):
    """Test User-Agent header requirement"""
    # Make request without User-Agent header and with security checks enabled
    response = security_test_client.get(
        "/api/v1/search",
        headers={
            "test_no_user_agent": "true",
            "X-Skip-Security-Checks": "false"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User-Agent header is required"

def test_invalid_scope(security_test_client, test_credentials):
    """Test scope validation"""
    # Mock the verify_token function to return invalid scope
    async def mock_verify_token(token: str) -> dict:
        return {
            "sub": test_credentials.client_id,
            "scopes": ["invalid.scope"],
            "refresh_token": test_credentials.refresh_token,
            "client_secret": test_credentials.client_secret
        }
    
    with patch("app.core.security.verify_token", mock_verify_token):
        response = security_test_client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": "Bearer test_token",
                "User-Agent": "Test Client",
                "X-Skip-Security-Checks": "false"
            }
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Invalid scope"

def test_brute_force_protection(security_test_client):
    """Test brute force protection middleware"""
    # Make multiple failed auth attempts
    for _ in range(6):  # Our limit is 5 attempts
        security_test_client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": "Bearer invalid_token",
                "User-Agent": "Test Client",
                "X-Skip-Security-Checks": "false"
            }
        )
    
    # Next attempt should be blocked
    response = security_test_client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer valid_token",
            "User-Agent": "Test Client",
            "X-Skip-Security-Checks": "false"
        }
    )
    assert response.status_code == 403
    assert "Too many failed attempts" in response.json()["detail"] 
