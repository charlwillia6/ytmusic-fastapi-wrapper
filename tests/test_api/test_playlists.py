from unittest.mock import patch
from app.schemas.models import PrivacyStatus

def test_get_playlist(authenticated_client):
    """Test get playlist endpoint"""
    mock_data = {"title": "Test Playlist"}
    with patch("app.services.ytmusic.YTMusicService.get_playlist", return_value=mock_data):
        response = authenticated_client.get(
            "/api/v1/playlists/test_playlist_id?limit=100&related=true&suggestions_limit=5"
        )
        assert response.status_code == 200
        assert response.json()["playlist"] == mock_data

def test_create_playlist(authenticated_client):
    """Test create playlist endpoint"""
    mock_data = "test_playlist_id"
    with patch("app.services.ytmusic.YTMusicService.create_playlist", return_value=mock_data):
        response = authenticated_client.post(
            "/api/v1/playlists/create",
            json={
                "title": "Test Playlist",
                "description": "Test Description",
                "privacy_status": PrivacyStatus.PRIVATE.value,
                "video_ids": ["test_video_1", "test_video_2"],
                "source_playlist": None
            }
        )
        assert response.status_code == 200
        assert response.json()["playlist_id"] == mock_data

def test_create_playlist_with_source(authenticated_client):
    """Test create playlist from source endpoint"""
    mock_data = "test_playlist_id"
    with patch("app.services.ytmusic.YTMusicService.create_playlist", return_value=mock_data):
        response = authenticated_client.post(
            "/api/v1/playlists/create",
            json={
                "title": "Test Playlist",
                "description": "Test Description",
                "privacy_status": PrivacyStatus.PRIVATE.value,
                "video_ids": None,
                "source_playlist": "source_playlist_id"
            }
        )
        assert response.status_code == 200
        assert response.json()["playlist_id"] == mock_data

def test_edit_playlist(authenticated_client):
    """Test edit playlist endpoint"""
    mock_data = "Playlist updated successfully"
    with patch("app.services.ytmusic.YTMusicService.edit_playlist", return_value=mock_data):
        response = authenticated_client.post(
            "/api/v1/playlists/test_playlist_id/edit",
            json={
                "title": "Updated Title",
                "description": "Updated Description",
                "privacy_status": PrivacyStatus.PUBLIC.value
            }
        )
        assert response.status_code == 200
        assert response.json()["message"] == mock_data

def test_edit_playlist_move_item(authenticated_client):
    """Test edit playlist with move item endpoint"""
    mock_data = "Playlist updated successfully"
    with patch("app.services.ytmusic.YTMusicService.edit_playlist", return_value=mock_data):
        response = authenticated_client.post(
            "/api/v1/playlists/test_playlist_id/edit",
            json={
                "move_item": ["video_id_1", "video_id_2"],
                "add_to_top": True
            }
        )
        assert response.status_code == 200
        assert response.json()["message"] == mock_data

def test_add_playlist_items(authenticated_client):
    """Test add playlist items endpoint"""
    mock_data = "Items added to playlist successfully"
    with patch("app.services.ytmusic.YTMusicService.add_playlist_items", return_value=mock_data):
        response = authenticated_client.post(
            "/api/v1/playlists/test_playlist_id/items",
            json={
                "video_ids": ["test_video_1", "test_video_2"],
                "duplicates": False
            }
        )
        assert response.status_code == 200
        assert response.json()["message"] == mock_data

def test_add_playlist_items_from_source(authenticated_client):
    """Test add playlist items from source endpoint"""
    mock_data = "Items added to playlist successfully"
    with patch("app.services.ytmusic.YTMusicService.add_playlist_items", return_value=mock_data):
        response = authenticated_client.post(
            "/api/v1/playlists/test_playlist_id/items",
            json={
                "video_ids": [],
                "source_playlist": "source_playlist_id",
                "duplicates": True
            }
        )
        assert response.status_code == 200
        assert response.json()["message"] == mock_data

def test_remove_playlist_items(authenticated_client):
    """Test remove playlist items endpoint"""
    mock_data = "Items removed from playlist successfully"
    with patch("app.services.ytmusic.YTMusicService.remove_playlist_items", return_value=mock_data):
        response = authenticated_client.delete(
            "/api/v1/playlists/test_playlist_id/items",
            json={
                "videos": [
                    {"setVideoId": "video_id_1"},
                    {"setVideoId": "video_id_2"}
                ]
            }
        )
        assert response.status_code == 200
        assert response.json()["message"] == mock_data

def test_delete_playlist(authenticated_client):
    """Test delete playlist endpoint"""
    mock_data = "Playlist deleted successfully"
    with patch("app.services.ytmusic.YTMusicService.delete_playlist", return_value=mock_data):
        response = authenticated_client.delete("/api/v1/playlists/test_playlist_id")
        assert response.status_code == 200
        assert response.json()["message"] == mock_data 
