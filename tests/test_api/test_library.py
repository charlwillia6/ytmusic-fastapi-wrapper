from unittest.mock import patch

def test_get_library_playlists(authenticated_client):
    """Test get library playlists endpoint"""
    mock_data = [{"title": "Test Playlist"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_playlists", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/playlists")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_songs(authenticated_client):
    """Test get library songs endpoint"""
    mock_data = [{"title": "Test Song"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_songs", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/songs?limit=25&validate_responses=false")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_songs_with_order(authenticated_client):
    """Test get library songs endpoint with order"""
    mock_data = [{"title": "Test Song"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_songs", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/songs?order=recently_added")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_albums(authenticated_client):
    """Test get library albums endpoint"""
    mock_data = [{"title": "Test Album"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_albums", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/albums")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_artists(authenticated_client):
    """Test get library artists endpoint"""
    mock_data = [{"name": "Test Artist"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_artists", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/artists")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_subscriptions(authenticated_client):
    """Test get library subscriptions endpoint"""
    mock_data = [{"name": "Test Channel"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_subscriptions", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/subscriptions")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_channels(authenticated_client):
    """Test get library channels endpoint"""
    mock_data = [{"name": "Test Channel"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_channels", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/channels")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_liked_songs(authenticated_client):
    """Test get liked songs endpoint"""
    mock_data = {"tracks": [{"title": "Liked Song"}]}
    with patch("app.services.ytmusic.YTMusicService.get_liked_songs", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/liked")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data["tracks"]

def test_get_history(authenticated_client):
    """Test get history endpoint"""
    mock_data = [{"title": "History Item"}]
    with patch("app.services.ytmusic.YTMusicService.get_history", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/history")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_add_history_item(authenticated_client):
    """Test add history item endpoint"""
    mock_song = {"videoId": "test_id", "title": "Test Song"}
    with patch("app.services.ytmusic.YTMusicService.get_song", return_value=mock_song), \
         patch("app.services.ytmusic.YTMusicService.add_history_item", return_value=True):
        response = authenticated_client.post("/api/v1/library/history/add", json={"video_id": "test_id"})
        assert response.status_code == 200
        assert response.json()["message"] == "History item added successfully"

def test_remove_history_items(authenticated_client):
    """Test remove history items endpoint"""
    with patch("app.services.ytmusic.YTMusicService.remove_history_items", return_value=True):
        response = authenticated_client.post("/api/v1/library/history/remove", json={"feedback_tokens": ["test_token"]})
        assert response.status_code == 200
        assert response.json()["message"] == "History items removed successfully"

def test_get_library_upload_songs(authenticated_client):
    """Test get library upload songs endpoint"""
    mock_data = [{"title": "Test Upload Song"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_upload_songs", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/uploads/songs")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_upload_artists(authenticated_client):
    """Test get library upload artists endpoint"""
    mock_data = [{"name": "Test Upload Artist"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_upload_artists", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/uploads/artists")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_upload_albums(authenticated_client):
    """Test get library upload albums endpoint"""
    mock_data = [{"title": "Test Upload Album"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_upload_albums", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/uploads/albums")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_upload_artist(authenticated_client):
    """Test get library upload artist endpoint"""
    mock_data = [{"title": "Test Upload Artist Songs"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_upload_artist", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/uploads/artist/test_browse_id")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_upload_album(authenticated_client):
    """Test get library upload album endpoint"""
    mock_data = {"title": "Test Upload Album"}
    with patch("app.services.ytmusic.YTMusicService.get_library_upload_album", return_value=mock_data):
        response = authenticated_client.get("/api/v1/library/uploads/album/test_browse_id")
        assert response.status_code == 200
        assert response.json() == mock_data

def test_upload_song(authenticated_client):
    """Test upload song endpoint"""
    with patch("app.services.ytmusic.YTMusicService.upload_song", return_value=True):
        response = authenticated_client.post("/api/v1/library/uploads/song", json={"filepath": "test.mp3"})
        assert response.status_code == 200
        assert response.json()["message"] == "Song uploaded successfully"

def test_delete_upload_entity(authenticated_client):
    """Test delete upload entity endpoint"""
    with patch("app.services.ytmusic.YTMusicService.delete_upload_entity", return_value=True):
        response = authenticated_client.delete("/api/v1/library/uploads/test_entity_id")
        assert response.status_code == 200
        assert response.json()["message"] == "Entity deleted successfully" 
