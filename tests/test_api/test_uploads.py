from unittest.mock import patch

def test_get_library_upload_songs(authenticated_client):
    """Test get library upload songs endpoint"""
    mock_data = [{"title": "Test Upload Song"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_upload_songs", return_value=mock_data):
        response = authenticated_client.get("/api/v1/uploads/songs")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_upload_artists(authenticated_client):
    """Test get library upload artists endpoint"""
    mock_data = [{"name": "Test Upload Artist"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_upload_artists", return_value=mock_data):
        response = authenticated_client.get("/api/v1/uploads/artists")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_upload_albums(authenticated_client):
    """Test get library upload albums endpoint"""
    mock_data = [{"title": "Test Upload Album"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_upload_albums", return_value=mock_data):
        response = authenticated_client.get("/api/v1/uploads/albums")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_upload_artist(authenticated_client):
    """Test get library upload artist endpoint"""
    mock_data = [{"title": "Test Upload Artist Songs"}]
    with patch("app.services.ytmusic.YTMusicService.get_library_upload_artist", return_value=mock_data):
        response = authenticated_client.get("/api/v1/uploads/artists/test_browse_id")
        assert response.status_code == 200
        assert response.json()["results"] == mock_data

def test_get_library_upload_album(authenticated_client):
    """Test get library upload album endpoint"""
    mock_data = {"title": "Test Upload Album"}
    with patch("app.services.ytmusic.YTMusicService.get_library_upload_album", return_value=mock_data):
        response = authenticated_client.get("/api/v1/uploads/albums/test_browse_id")
        assert response.status_code == 200
        assert response.json()["album"] == mock_data

def test_upload_song(authenticated_client):
    """Test upload song endpoint"""
    with patch("app.services.ytmusic.YTMusicService.upload_song", return_value=True):
        response = authenticated_client.post("/api/v1/uploads/songs", json={"filepath": "test.mp3"})
        assert response.status_code == 200
        assert response.json()["message"] == "Song uploaded successfully"

def test_delete_upload_entity(authenticated_client):
    """Test delete upload entity endpoint"""
    with patch("app.services.ytmusic.YTMusicService.delete_upload_entity", return_value=True):
        response = authenticated_client.delete("/api/v1/uploads/entities/test_entity_id")
        assert response.status_code == 200
        assert response.json()["message"] == "Upload entity deleted successfully" 
