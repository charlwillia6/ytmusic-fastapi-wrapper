from unittest.mock import patch
from app.api.v1.endpoints.search import SearchFilter, SearchScope

def test_search(authenticated_client):
    """Test search endpoint"""
    mock_data = [{"title": "Test Result"}]
    with patch("app.services.ytmusic.YTMusicService.search", return_value=mock_data):
        response = authenticated_client.get(
            "/api/v1/search?query=test&filter=songs&scope=library&limit=20&ignore_spelling=false"
        )
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_search_with_filter(authenticated_client):
    """Test search endpoint with filter"""
    mock_data = [{"title": "Test Song"}]
    with patch("app.services.ytmusic.YTMusicService.search", return_value=mock_data):
        response = authenticated_client.get(
            f"/api/v1/search?query=test&filter={SearchFilter.SONGS.value}"
        )
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_search_with_scope(authenticated_client):
    """Test search endpoint with scope"""
    mock_data = [{"title": "Test Upload"}]
    with patch("app.services.ytmusic.YTMusicService.search", return_value=mock_data):
        response = authenticated_client.get(
            f"/api/v1/search?query=test&scope={SearchScope.UPLOADS.value}"
        )
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_search_suggestions(authenticated_client):
    """Test get search suggestions endpoint"""
    mock_data = ["suggestion1", "suggestion2"]
    with patch("app.services.ytmusic.YTMusicService.get_search_suggestions", return_value=mock_data):
        response = authenticated_client.get(
            "/api/v1/search/suggestions?query=test&detailed_runs=false"
        )
        assert response.status_code == 200
        assert response.json()["suggestions"] == mock_data

def test_search_suggestions_detailed(authenticated_client):
    """Test get search suggestions endpoint with detailed runs"""
    mock_data = [{"text": "suggestion1", "runs": []}, {"text": "suggestion2", "runs": []}]
    with patch("app.services.ytmusic.YTMusicService.get_search_suggestions", return_value=mock_data):
        response = authenticated_client.get(
            "/api/v1/search/suggestions?query=test&detailed_runs=true"
        )
        assert response.status_code == 200
        assert response.json()["suggestions"] == mock_data

def test_remove_search_suggestions(authenticated_client):
    """Test remove search suggestions endpoint"""
    with patch("app.services.ytmusic.YTMusicService.remove_search_suggestions", return_value=True):
        response = authenticated_client.post("/api/v1/search/suggestions/remove")
        assert response.status_code == 200
        assert response.json()["message"] == "Search suggestions removed successfully"

def test_remove_search_suggestions_failure(authenticated_client):
    """Test remove search suggestions endpoint failure"""
    with patch("app.services.ytmusic.YTMusicService.remove_search_suggestions", return_value=False):
        response = authenticated_client.post("/api/v1/search/suggestions/remove")
        assert response.status_code == 200
        assert response.json()["message"] == "Failed to remove search suggestions" 
