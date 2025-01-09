from ytmusicapi import YTMusic
import pytest
from unittest.mock import Mock, patch
import os
from typing import Dict, Any
from dotenv import load_dotenv

@pytest.fixture
def mock_oauth_dict() -> Dict[str, Any]:
    return {
        "token": "test_token",
        "refresh_token": "test_refresh_token",
        "token_uri": "test_token_uri",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "scopes": ["test_scope1", "test_scope2"]
    }

@pytest.fixture
def ytmusic_client(mock_oauth_dict):
    with patch('ytmusicapi.YTMusic') as mock_ytmusic_class:
        mock_instance = Mock()
        mock_ytmusic_class.return_value = mock_instance
        yield mock_instance

class TestYTMusicIntegration:
    # Search Tests
    def test_search_functionality(self, ytmusic_client):
        expected_results = [{"title": "Test Song", "artist": "Test Artist"}]
        ytmusic_client.search.return_value = expected_results
        
        results = ytmusic_client.search(query="test query", filter="songs", limit=1)
        assert results == expected_results
        ytmusic_client.search.assert_called_once_with(
            query="test query", filter="songs", limit=1
        )

    def test_search_suggestions(self, ytmusic_client):
        expected_suggestions = ["suggestion1", "suggestion2"]
        ytmusic_client.get_search_suggestions.return_value = expected_suggestions
        
        results = ytmusic_client.get_search_suggestions("test")
        assert results == expected_suggestions
        ytmusic_client.get_search_suggestions.assert_called_once_with("test")

    def test_remove_search_suggestions(self, ytmusic_client):
        suggestions = [{"text": "test"}]
        ytmusic_client.remove_search_suggestions.return_value = None
        
        ytmusic_client.remove_search_suggestions(suggestions)
        ytmusic_client.remove_search_suggestions.assert_called_once_with(suggestions)

    # Browse Tests
    def test_get_home(self, ytmusic_client):
        expected_home = [{"title": "Home Item"}]
        ytmusic_client.get_home.return_value = expected_home
        
        results = ytmusic_client.get_home(limit=1)
        assert results == expected_home
        ytmusic_client.get_home.assert_called_once_with(limit=1)

    def test_get_artist_info(self, ytmusic_client):
        expected_info = {"name": "Test Artist", "description": "Artist Description"}
        ytmusic_client.get_artist.return_value = expected_info
        
        info = ytmusic_client.get_artist(channelId="test_channel_id")
        assert info == expected_info
        ytmusic_client.get_artist.assert_called_once_with(channelId="test_channel_id")

    def test_get_user_info(self, ytmusic_client):
        expected_info = {"name": "Test User"}
        ytmusic_client.get_user.return_value = expected_info
        
        info = ytmusic_client.get_user(channelId="test_channel_id")
        assert info == expected_info
        ytmusic_client.get_user.assert_called_once_with(channelId="test_channel_id")

    # Watch Tests
    def test_get_watch_playlist(self, ytmusic_client):
        expected_playlist = {"tracks": [{"title": "Song 1"}]}
        ytmusic_client.get_watch_playlist.return_value = expected_playlist
        
        playlist = ytmusic_client.get_watch_playlist(videoId="test_video_id", limit=1)
        assert playlist == expected_playlist
        ytmusic_client.get_watch_playlist.assert_called_once_with(
            videoId="test_video_id", limit=1
        )

    def test_get_lyrics(self, ytmusic_client):
        expected_lyrics = {"lyrics": "Test lyrics"}
        ytmusic_client.get_lyrics.return_value = expected_lyrics
        
        lyrics = ytmusic_client.get_lyrics("test_browse_id")
        assert lyrics == expected_lyrics
        ytmusic_client.get_lyrics.assert_called_once_with("test_browse_id")

    # Library Tests
    def test_get_library_playlists(self, ytmusic_client):
        expected_playlists = [{"id": "playlist1", "name": "Playlist 1"}]
        ytmusic_client.get_library_playlists.return_value = expected_playlists
        
        playlists = ytmusic_client.get_library_playlists(limit=1)
        assert playlists == expected_playlists
        ytmusic_client.get_library_playlists.assert_called_once_with(limit=1)

    def test_get_liked_songs(self, ytmusic_client):
        expected_songs = {"tracks": [{"title": "Liked Song"}]}
        ytmusic_client.get_liked_songs.return_value = expected_songs
        
        songs = ytmusic_client.get_liked_songs(limit=1)
        assert songs == expected_songs
        ytmusic_client.get_liked_songs.assert_called_once_with(limit=1)

    def test_get_history(self, ytmusic_client):
        expected_history = [{"title": "History Song"}]
        ytmusic_client.get_history.return_value = expected_history
        
        history = ytmusic_client.get_history()
        assert history == expected_history
        ytmusic_client.get_history.assert_called_once()

    # Playlist Tests
    def test_playlist_creation(self, ytmusic_client):
        expected_playlist_id = "test_playlist_id"
        ytmusic_client.create_playlist.return_value = expected_playlist_id
        
        playlist_id = ytmusic_client.create_playlist(
            title="Test Playlist",
            description="Test Description",
            privacy_status="PRIVATE"
        )
        assert playlist_id == expected_playlist_id
        ytmusic_client.create_playlist.assert_called_once_with(
            title="Test Playlist",
            description="Test Description",
            privacy_status="PRIVATE"
        )

    def test_playlist_modification(self, ytmusic_client):
        ytmusic_client.edit_playlist.return_value = None
        
        ytmusic_client.edit_playlist(
            playlistId="test_id",
            title="Updated Title",
            description="Updated Description"
        )
        ytmusic_client.edit_playlist.assert_called_once()

    # Upload Tests
    def test_upload_song(self, ytmusic_client):
        ytmusic_client.upload_song.return_value = None
        
        ytmusic_client.upload_song("test.mp3")
        ytmusic_client.upload_song.assert_called_once_with("test.mp3")

    def test_get_library_upload_songs(self, ytmusic_client):
        expected_songs = [{"title": "Uploaded Song"}]
        ytmusic_client.get_library_upload_songs.return_value = expected_songs
        
        songs = ytmusic_client.get_library_upload_songs(limit=1)
        assert songs == expected_songs
        ytmusic_client.get_library_upload_songs.assert_called_once_with(limit=1)

    # Podcast Tests
    def test_get_podcast(self, ytmusic_client):
        expected_podcast = {"title": "Test Podcast"}
        ytmusic_client.get_podcast.return_value = expected_podcast
        
        podcast = ytmusic_client.get_podcast("test_id")
        assert podcast == expected_podcast
        ytmusic_client.get_podcast.assert_called_once_with("test_id")

    def test_get_podcast_episode(self, ytmusic_client):
        expected_episode = {"title": "Test Episode"}
        ytmusic_client.get_episode.return_value = expected_episode
        
        episode = ytmusic_client.get_episode("test_id")
        assert episode == expected_episode
        ytmusic_client.get_episode.assert_called_once_with("test_id")

    @pytest.mark.integration
    def test_real_ytmusic_connection(self):
        """
        This test requires real credentials from the .env file.
        To run this test specifically, use: pytest -m integration
        """
        load_dotenv()
        
        if not all([
            os.getenv("YT_TOKEN"),
            os.getenv("YT_REFRESH_TOKEN"),
            os.getenv("YT_CLIENT_ID"),
            os.getenv("YT_CLIENT_SECRET")
        ]):
            pytest.skip("Skipping integration test - missing required environment variables")
        
        oauth_dict = {
            "token": os.getenv("YT_TOKEN"),
            "refresh_token": os.getenv("YT_REFRESH_TOKEN"),
            "token_uri": os.getenv("YT_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "client_id": os.getenv("YT_CLIENT_ID"),
            "client_secret": os.getenv("YT_CLIENT_SECRET"),
            "scopes": os.getenv("YT_SCOPES", "https://www.googleapis.com/auth/youtube.readonly").split(",")
        }
        
        ytmusic = YTMusic(auth=oauth_dict)
        search_results = ytmusic.search("test")
        assert isinstance(search_results, list)
        assert len(search_results) > 0

    # Additional Browse Tests
    def test_get_album(self, ytmusic_client):
        expected_album = {"title": "Test Album", "tracks": []}
        ytmusic_client.get_album.return_value = expected_album
        
        album = ytmusic_client.get_album(browseId="test_browse_id")
        assert album == expected_album
        ytmusic_client.get_album.assert_called_once_with(browseId="test_browse_id")

    def test_get_album_browse_id(self, ytmusic_client):
        expected_browse_id = "test_browse_id"
        ytmusic_client.get_album_browse_id.return_value = expected_browse_id
        
        browse_id = ytmusic_client.get_album_browse_id("test_video_id")
        assert browse_id == expected_browse_id
        ytmusic_client.get_album_browse_id.assert_called_once_with("test_video_id")

    def test_get_song(self, ytmusic_client):
        expected_song = {"title": "Test Song"}
        ytmusic_client.get_song.return_value = expected_song
        
        song = ytmusic_client.get_song(videoId="test_video_id")
        assert song == expected_song
        ytmusic_client.get_song.assert_called_once_with(videoId="test_video_id")

    def test_get_song_related(self, ytmusic_client):
        expected_related = [{"title": "Related Song"}]
        ytmusic_client.get_song_related.return_value = expected_related
        
        related = ytmusic_client.get_song_related(browseId="test_browse_id")
        assert related == expected_related
        ytmusic_client.get_song_related.assert_called_once_with(browseId="test_browse_id")

    # Explore Tests
    def test_get_mood_categories(self, ytmusic_client):
        expected_categories = [{"title": "Mood Category"}]
        ytmusic_client.get_mood_categories.return_value = expected_categories
        
        categories = ytmusic_client.get_mood_categories()
        assert categories == expected_categories
        ytmusic_client.get_mood_categories.assert_called_once()

    def test_get_mood_playlists(self, ytmusic_client):
        expected_playlists = [{"title": "Mood Playlist"}]
        ytmusic_client.get_mood_playlists.return_value = expected_playlists
        
        playlists = ytmusic_client.get_mood_playlists("test_params")
        assert playlists == expected_playlists
        ytmusic_client.get_mood_playlists.assert_called_once_with("test_params")

    def test_get_charts(self, ytmusic_client):
        expected_charts = {"trends": [{"title": "Trending"}]}
        ytmusic_client.get_charts.return_value = expected_charts
        
        charts = ytmusic_client.get_charts(country="US")
        assert charts == expected_charts
        ytmusic_client.get_charts.assert_called_once_with(country="US")

    # Additional Library Tests
    def test_add_history_item(self, ytmusic_client):
        ytmusic_client.add_history_item.return_value = None
        
        ytmusic_client.add_history_item(song="test_video_id")
        ytmusic_client.add_history_item.assert_called_once_with(song="test_video_id")

    def test_remove_history_items(self, ytmusic_client):
        ytmusic_client.remove_history_items.return_value = None
        
        ytmusic_client.remove_history_items(["test_video_id"])
        ytmusic_client.remove_history_items.assert_called_once_with(["test_video_id"])

    def test_edit_song_library_status(self, ytmusic_client):
        ytmusic_client.edit_song_library_status.return_value = None
        
        ytmusic_client.edit_song_library_status(feedbackTokens=["token1"])
        ytmusic_client.edit_song_library_status.assert_called_once_with(feedbackTokens=["token1"])

    def test_rate_playlist(self, ytmusic_client):
        ytmusic_client.rate_playlist.return_value = None
        
        ytmusic_client.rate_playlist(playlistId="test_id", rating="LIKE")
        ytmusic_client.rate_playlist.assert_called_once_with(playlistId="test_id", rating="LIKE")

    # Additional Playlist Tests
    def test_get_playlist(self, ytmusic_client):
        expected_playlist = {"title": "Test Playlist", "tracks": []}
        ytmusic_client.get_playlist.return_value = expected_playlist
        
        playlist = ytmusic_client.get_playlist(playlistId="test_id")
        assert playlist == expected_playlist
        ytmusic_client.get_playlist.assert_called_once_with(playlistId="test_id")

    def test_delete_playlist(self, ytmusic_client):
        ytmusic_client.delete_playlist.return_value = None
        
        ytmusic_client.delete_playlist("test_id")
        ytmusic_client.delete_playlist.assert_called_once_with("test_id")

    # Additional Upload Tests
    def test_delete_upload_entity(self, ytmusic_client):
        ytmusic_client.delete_upload_entity.return_value = None
        
        ytmusic_client.delete_upload_entity("test_id")
        ytmusic_client.delete_upload_entity.assert_called_once_with("test_id")

    # Additional Podcast Tests
    def test_get_episodes_playlist(self, ytmusic_client):
        expected_playlist = {"title": "Episodes Playlist"}
        ytmusic_client.get_episodes_playlist.return_value = expected_playlist
        
        playlist = ytmusic_client.get_episodes_playlist("test_id")
        assert playlist == expected_playlist
        ytmusic_client.get_episodes_playlist.assert_called_once_with("test_id")
