from unittest.mock import patch
import pytest
from app.services.ytmusic import YTMusicService
from app.schemas.models import CredentialsModel

@pytest.fixture
def ytmusic_service() -> YTMusicService:
    """Create a YTMusicService instance for testing"""
    credentials = CredentialsModel(
        token="test_token",
        refresh_token="test_refresh_token",
        token_uri="test_token_uri",
        client_id="test_client_id",
        client_secret="test_client_secret",
        scopes=["https://www.googleapis.com/auth/youtube.readonly"]
    )
    return YTMusicService(credentials)

def test_search(ytmusic_service) -> None:
    """Test search method"""
    mock_results = [
        {"id": "1", "title": "Result 1", "type": "song"},
        {"id": "2", "title": "Result 2", "type": "video"}
    ]
    
    with patch("ytmusicapi.YTMusic.search", return_value=mock_results):
        results = ytmusic_service.search("test query", filter="songs", limit=20)
        assert isinstance(results, list)
        assert results == mock_results

def test_get_library_playlists(ytmusic_service) -> None:
    """Test get_library_playlists method"""
    mock_playlists = [
        {"id": "1", "title": "Playlist 1"},
        {"id": "2", "title": "Playlist 2"}
    ]
    
    with patch("ytmusicapi.YTMusic.get_library_playlists", return_value=mock_playlists):
        playlists = ytmusic_service.get_library_playlists()
        assert isinstance(playlists, list)
        assert playlists == mock_playlists

def test_get_playlist(ytmusic_service) -> None:
    """Test get_playlist method"""
    mock_playlist = {
        "title": "Test Playlist",
        "author": "Test Author",
        "description": "Playlist description",
        "tracks": []
    }
    
    with patch("ytmusicapi.YTMusic.get_playlist", return_value=mock_playlist):
        playlist = ytmusic_service.get_playlist("test_playlist_id")
        assert isinstance(playlist, dict)
        assert playlist == mock_playlist

def test_get_artist(ytmusic_service) -> None:
    """Test get_artist method"""
    mock_artist = {
        "name": "Test Artist",
        "description": "Artist description",
        "songs": [],
        "albums": []
    }
    
    with patch("ytmusicapi.YTMusic.get_artist", return_value=mock_artist):
        artist = ytmusic_service.get_artist("test_channel_id")
        assert isinstance(artist, dict)
        assert artist == mock_artist

def test_get_album(ytmusic_service) -> None:
    """Test get_album method"""
    mock_album = {
        "title": "Test Album",
        "artist": "Test Artist",
        "year": "2023",
        "tracks": []
    }
    
    with patch("ytmusicapi.YTMusic.get_album", return_value=mock_album):
        album = ytmusic_service.get_album("test_browse_id")
        assert isinstance(album, dict)
        assert album == mock_album

def test_get_song(ytmusic_service) -> None:
    """Test get_song method"""
    mock_song = {
        "videoId": "test_video_id",
        "title": "Test Song",
        "artists": [{"name": "Test Artist"}],
        "album": "Test Album"
    }
    
    with patch("ytmusicapi.YTMusic.get_song", return_value=mock_song):
        song = ytmusic_service.get_song("test_video_id")
        assert isinstance(song, dict)
        assert song == mock_song

def test_get_liked_songs(ytmusic_service) -> None:
    """Test get_liked_songs method"""
    mock_songs = [
        {"id": "1", "title": "Liked Song 1"},
        {"id": "2", "title": "Liked Song 2"}
    ]
    
    with patch("ytmusicapi.YTMusic.get_liked_songs", return_value=mock_songs):
        songs = ytmusic_service.get_liked_songs()
        assert isinstance(songs, list)
        assert songs == mock_songs

def test_get_history(ytmusic_service) -> None:
    """Test get_history method"""
    mock_history = [
        {"id": "1", "title": "History Item 1"},
        {"id": "2", "title": "History Item 2"}
    ]
    
    with patch("ytmusicapi.YTMusic.get_history", return_value=mock_history):
        history = ytmusic_service.get_history()
        assert isinstance(history, list)
        assert history == mock_history

def test_add_history_item(ytmusic_service) -> None:
    """Test add_history_item method"""
    with patch("ytmusicapi.YTMusic.add_history_item", return_value=True):
        result = ytmusic_service.add_history_item("test_video_id")
        assert isinstance(result, bool)
        assert result is True

def test_remove_history_items(ytmusic_service) -> None:
    """Test remove_history_items method"""
    with patch("ytmusicapi.YTMusic.remove_history_items", return_value=True):
        result = ytmusic_service.remove_history_items(["test_video_id_1", "test_video_id_2"])
        assert isinstance(result, bool)
        assert result is True

def test_get_channel(ytmusic_service) -> None:
    """Test get_channel method"""
    mock_channel = {
        "description": "Channel description",
        "name": "Test Channel",
        "episodes": []
    }
    
    with patch("ytmusicapi.YTMusic.get_channel", return_value=mock_channel):
        channel = ytmusic_service.get_channel("test_channel_id")
        assert isinstance(channel, dict)
        assert channel == mock_channel

def test_get_channel_episodes(ytmusic_service) -> None:
    """Test get_channel_episodes method"""
    mock_episodes = [
        {"id": "1", "title": "Episode 1"},
        {"id": "2", "title": "Episode 2"}
    ]
    
    with patch("ytmusicapi.YTMusic.get_channel_episodes", return_value=mock_episodes):
        episodes = ytmusic_service.get_channel_episodes("test_channel_id", "test_params")
        assert isinstance(episodes, list)
        assert episodes == mock_episodes

def test_get_podcast(ytmusic_service) -> None:
    """Test get_podcast method"""
    mock_podcast = {
        "author": "Test Author",
        "description": "Podcast description",
        "episodes": []
    }
    
    with patch("ytmusicapi.YTMusic.get_podcast", return_value=mock_podcast):
        podcast = ytmusic_service.get_podcast("test_playlist_id")
        assert isinstance(podcast, dict)
        assert podcast == mock_podcast

def test_get_episode(ytmusic_service) -> None:
    """Test get_episode method"""
    mock_episode = {
        "description": "Episode description",
        "title": "Test Episode",
        "duration": "10:00"
    }
    
    with patch("ytmusicapi.YTMusic.get_episode", return_value=mock_episode):
        episode = ytmusic_service.get_episode("test_video_id")
        assert isinstance(episode, dict)
        assert episode == mock_episode

def test_get_episodes_playlist(ytmusic_service) -> None:
    """Test get_episodes_playlist method"""
    mock_playlist = {
        "title": "Episodes Playlist",
        "episodes": []
    }
    
    with patch("ytmusicapi.YTMusic.get_episodes_playlist", return_value=mock_playlist):
        playlist = ytmusic_service.get_episodes_playlist()
        assert isinstance(playlist, dict)
        assert playlist == mock_playlist

def test_get_library_podcasts(ytmusic_service) -> None:
    """Test get_library_podcasts method"""
    mock_podcasts = [
        {"id": "1", "title": "Podcast 1"},
        {"id": "2", "title": "Podcast 2"}
    ]
    
    with patch("ytmusicapi.YTMusic.get_library_podcasts", return_value=mock_podcasts):
        podcasts = ytmusic_service.get_library_podcasts()
        assert isinstance(podcasts, list)
        assert podcasts == mock_podcasts

def test_get_saved_episodes(ytmusic_service) -> None:
    """Test get_saved_episodes method"""
    mock_episodes = [
        {"id": "1", "title": "Saved Episode 1"},
        {"id": "2", "title": "Saved Episode 2"}
    ]
    
    with patch("ytmusicapi.YTMusic.get_saved_episodes", return_value=mock_episodes):
        episodes = ytmusic_service.get_saved_episodes()
        assert isinstance(episodes, list)
        assert episodes == mock_episodes

def test_get_user_videos(ytmusic_service) -> None:
    """Test get_user_videos method"""
    mock_videos = [
        {"id": "1", "title": "Video 1"},
        {"id": "2", "title": "Video 2"}
    ]
    
    with patch("ytmusicapi.YTMusic.get_user_videos", return_value=mock_videos):
        videos = ytmusic_service.get_user_videos("test_channel_id", "test_params")
        assert isinstance(videos, list)
        assert videos == mock_videos

def test_get_library_channels(ytmusic_service) -> None:
    """Test get_library_channels method"""
    mock_channels = [
        {"id": "1", "title": "Channel 1"},
        {"id": "2", "title": "Channel 2"}
    ]
    
    with patch("ytmusicapi.YTMusic.get_library_channels", return_value=mock_channels):
        channels = ytmusic_service.get_library_channels()
        assert isinstance(channels, list)
        assert channels == mock_channels 
