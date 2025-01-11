from unittest.mock import patch

def test_get_channel(authenticated_client):
    """Test get channel endpoint"""
    mock_data = {"name": "Test Channel", "description": "Test Description"}
    with patch("app.services.ytmusic.YTMusicService.get_channel", return_value=mock_data):
        response = authenticated_client.get("/api/v1/podcasts/channel/test_channel_id")
        assert response.status_code == 200
        assert response.json() == mock_data

def test_get_channel_episodes(authenticated_client):
    """Test get channel episodes endpoint"""
    mock_data = [{"title": "Test Episode"}]
    with patch("app.services.ytmusic.YTMusicService.get_channel_episodes", return_value=mock_data):
        response = authenticated_client.get("/api/v1/podcasts/channel/test_channel_id/episodes?params=test_params")
        assert response.status_code == 200
        assert response.json() == mock_data

def test_get_podcast(authenticated_client):
    """Test get podcast endpoint"""
    mock_data = {"title": "Test Podcast", "episodes": []}
    with patch("app.services.ytmusic.YTMusicService.get_podcast", return_value=mock_data):
        response = authenticated_client.get("/api/v1/podcasts/podcast/test_playlist_id?limit=100")
        assert response.status_code == 200
        assert response.json() == mock_data

def test_get_episode(authenticated_client):
    """Test get episode endpoint"""
    mock_data = {"title": "Test Episode", "description": "Test Description"}
    with patch("app.services.ytmusic.YTMusicService.get_episode", return_value=mock_data):
        response = authenticated_client.get("/api/v1/podcasts/episode/test_video_id")
        assert response.status_code == 200
        assert response.json() == mock_data

def test_get_episodes_playlist(authenticated_client):
    """Test get episodes playlist endpoint"""
    mock_data = {"title": "Episodes Playlist", "episodes": []}
    with patch("app.services.ytmusic.YTMusicService.get_episodes_playlist", return_value=mock_data):
        response = authenticated_client.get("/api/v1/podcasts/episodes/playlist/RDPN")
        assert response.status_code == 200
        assert response.json() == mock_data

def test_get_library_podcasts(authenticated_client):
    """Test get library podcasts endpoint"""
    mock_data = [{"title": "Test Library Podcast"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_podcasts", return_value=mock_data):
        response = authenticated_client.get("/api/v1/podcasts/library?limit=25")
        assert response.status_code == 200
        assert response.json() == mock_data

def test_get_library_podcasts_with_order(authenticated_client):
    """Test get library podcasts endpoint with order"""
    mock_data = [{"title": "Test Library Podcast"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_podcasts", return_value=mock_data):
        response = authenticated_client.get(
            "/api/v1/podcasts/library?limit=25&order=recently_added"
        )
        assert response.status_code == 200
        assert response.json() == mock_data

def test_get_saved_episodes(authenticated_client):
    """Test get saved episodes endpoint"""
    mock_data = {"title": "Saved Episodes", "episodes": []}
    with patch("app.services.ytmusic.YTMusicService.get_saved_episodes", return_value=mock_data):
        response = authenticated_client.get("/api/v1/podcasts/saved-episodes?limit=100")
        assert response.status_code == 200
        assert response.json() == mock_data 
