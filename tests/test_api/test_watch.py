from unittest.mock import patch

def test_get_watch_playlist(authenticated_client):
    """Test get watch playlist endpoint"""
    mock_data = {"title": "Test Watch Playlist"}
    with patch("app.services.ytmusic.YTMusicService.get_watch_playlist", return_value=mock_data):
        response = authenticated_client.get(
            "/api/v1/watch/playlist?video_id=test_video_id&limit=25&radio=false&shuffle=false"
        )
        assert response.status_code == 200
        assert response.json()["playlist"] == mock_data

def test_get_watch_playlist_with_playlist_id(authenticated_client):
    """Test get watch playlist endpoint with playlist ID"""
    mock_data = {"title": "Test Watch Playlist"}
    with patch("app.services.ytmusic.YTMusicService.get_watch_playlist", return_value=mock_data):
        response = authenticated_client.get(
            "/api/v1/watch/playlist?playlist_id=test_playlist_id&limit=25&radio=true&shuffle=true"
        )
        assert response.status_code == 200
        assert response.json()["playlist"] == mock_data

def test_get_lyrics(authenticated_client):
    """Test get lyrics endpoint"""
    mock_data = {"text": "Test lyrics"}
    with patch("app.services.ytmusic.YTMusicService.get_lyrics", return_value=mock_data):
        response = authenticated_client.get("/api/v1/watch/lyrics/test_browse_id")
        assert response.status_code == 200
        assert response.json()["lyrics"] == mock_data 
