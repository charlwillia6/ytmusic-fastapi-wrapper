from unittest.mock import patch

def test_get_mood_categories(authenticated_client):
    """Test get mood categories endpoint"""
    mock_data = [{"title": "Test Mood"}]
    with patch("app.services.ytmusic.YTMusicService.get_mood_categories", return_value=mock_data):
        response = authenticated_client.get("/api/v1/explore/moods")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_mood_playlists(authenticated_client):
    """Test get mood playlists endpoint"""
    mock_data = [{"title": "Test Playlist"}]
    with patch("app.services.ytmusic.YTMusicService.get_mood_playlists", return_value=mock_data):
        response = authenticated_client.get("/api/v1/explore/moods/test_params")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_charts(authenticated_client):
    """Test get charts endpoint"""
    mock_data = {"charts": [{"title": "Test Chart"}]}
    with patch("app.services.ytmusic.YTMusicService.get_charts", return_value=mock_data):
        response = authenticated_client.get("/api/v1/explore/charts?country_code=US")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_charts_default_country(authenticated_client):
    """Test get charts endpoint with default country code"""
    mock_data = {"title": "Test Charts"}
    with patch("app.services.ytmusic.YTMusicService.get_charts", return_value=mock_data):
        response = authenticated_client.get("/api/v1/explore/charts")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data 
