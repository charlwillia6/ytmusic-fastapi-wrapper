from unittest.mock import patch

def test_get_home(authenticated_client):
    """Test get home endpoint"""
    mock_data = [{"title": "Test Home Section"}]
    with patch("app.services.ytmusic.YTMusicService.get_home", return_value=mock_data):
        response = authenticated_client.get("/api/v1/browse/home")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_artist(authenticated_client):
    """Test get artist endpoint"""
    mock_data = {"name": "Test Artist"}
    with patch("app.services.ytmusic.YTMusicService.get_artist", return_value=mock_data):
        response = authenticated_client.get("/api/v1/browse/artists/test_channel_id")
        assert response.status_code == 200
        assert response.json()["artist"] == mock_data

def test_get_artist_with_browse_id(authenticated_client):
    """Test get artist endpoint with browse_id"""
    mock_data = {"name": "Test Artist"}
    with patch("app.services.ytmusic.YTMusicService.get_artist", return_value=mock_data):
        response = authenticated_client.get("/api/v1/browse/artists/test_channel_id?browse_id=test_browse_id")
        assert response.status_code == 200
        assert response.json()["artist"] == mock_data

def test_get_artist_albums(authenticated_client):
    """Test get artist albums endpoint"""
    mock_data = {"albums": [{"title": "Test Album"}]}
    with patch("app.services.ytmusic.YTMusicService.get_artist_albums", return_value=mock_data):
        response = authenticated_client.get(
            "/api/v1/browse/artists/test_channel_id/albums?limit=10&order=Recency&params=test_params"
        )
        assert response.status_code == 200
        assert response.json()["albums"] == mock_data

def test_get_album(authenticated_client):
    """Test get album endpoint"""
    mock_data = {"title": "Test Album"}
    with patch("app.services.ytmusic.YTMusicService.get_album", return_value=mock_data):
        response = authenticated_client.get("/api/v1/browse/albums/test_browse_id")
        assert response.status_code == 200
        assert response.json()["album"] == mock_data

def test_get_album_browse_id(authenticated_client):
    """Test get album browse ID endpoint"""
    mock_data = "test_browse_id"
    with patch("app.services.ytmusic.YTMusicService.get_album_browse_id", return_value=mock_data):
        response = authenticated_client.get("/api/v1/browse/albums/browse/test_audio_playlist_id")
        assert response.status_code == 200
        assert response.json()["browse_id"] == mock_data

def test_get_user(authenticated_client):
    """Test get user endpoint"""
    mock_data = {"name": "Test User"}
    with patch("app.services.ytmusic.YTMusicService.get_user", return_value=mock_data):
        response = authenticated_client.get("/api/v1/browse/users/test_channel_id")
        assert response.status_code == 200
        assert response.json()["user"] == mock_data

def test_get_user_playlists(authenticated_client):
    """Test get user playlists endpoint"""
    mock_data = [{"title": "Test Playlist"}]
    with patch("app.services.ytmusic.YTMusicService.get_user_playlists", return_value=mock_data):
        response = authenticated_client.get("/api/v1/browse/users/test_channel_id/playlists?params=test_params")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_user_videos(authenticated_client):
    """Test get user videos endpoint"""
    mock_data = [{"title": "Test Video"}]
    with patch("app.services.ytmusic.YTMusicService.get_user_videos", return_value=mock_data):
        response = authenticated_client.get("/api/v1/browse/users/test_channel_id/videos?params=test_params")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_playlist(authenticated_client):
    """Test get playlist endpoint"""
    mock_data = {"title": "Test Playlist"}
    with patch("app.services.ytmusic.YTMusicService.get_playlist", return_value=mock_data):
        response = authenticated_client.get(
            "/api/v1/browse/playlists/test_playlist_id?limit=10&related=true&suggestions_limit=5"
        )
        assert response.status_code == 200
        assert response.json()["playlist"] == mock_data

def test_get_song(authenticated_client):
    """Test get song endpoint"""
    mock_data = {"title": "Test Song"}
    with patch("app.services.ytmusic.YTMusicService.get_song", return_value=mock_data):
        response = authenticated_client.get("/api/v1/browse/songs/test_video_id")
        assert response.status_code == 200
        assert response.json()["song"] == mock_data

def test_get_song_related(authenticated_client):
    """Test get related songs endpoint"""
    mock_data = {"songs": [{"title": "Related Song"}]}
    with patch("app.services.ytmusic.YTMusicService.get_song_related", return_value=mock_data):
        response = authenticated_client.get("/api/v1/browse/songs/test_browse_id/related")
        assert response.status_code == 200
        assert response.json()["related"] == mock_data

def test_get_tasteprofile(authenticated_client):
    """Test get taste profile endpoint"""
    mock_data = {"genres": ["Rock", "Jazz"]}
    with patch("app.services.ytmusic.YTMusicService.get_tasteprofile", return_value=mock_data):
        response = authenticated_client.get("/api/v1/browse/tasteprofile")
        assert response.status_code == 200
        assert response.json()["profile"] == mock_data

def test_set_tasteprofile(authenticated_client):
    """Test set taste profile endpoint"""
    artists = ["Artist 1", "Artist 2"]
    with patch("app.services.ytmusic.YTMusicService.set_tasteprofile", return_value=True):
        response = authenticated_client.post("/api/v1/browse/tasteprofile", json=artists)
        assert response.status_code == 200
        assert response.json()["message"] == "Taste profile updated successfully" 
