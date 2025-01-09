from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, Mock
import os
from database import SessionLocal, Base, Credentials, Session as DBSession
from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

def get_test_app():
    # Set environment variables
    os.environ["GOOGLE_CLIENT_ID"] = "test_client_id"
    os.environ["GOOGLE_CLIENT_SECRET"] = "test_client_secret"
    os.environ["GOOGLE_REDIRECT_URI"] = "http://localhost:8000/callback"
    
    # Import and return the app
    from main import app, get_db
    return app, get_db

# Get app and get_db function
app, get_db = get_test_app()

@pytest.fixture(scope="function")
def test_db():
    # Create an in-memory database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for testing
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.rollback()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

# Helper function
def create_test_session(test_db: Session) -> str:
    try:
        # Create test credentials
        test_credentials = Credentials(
            token="test_token",
            refresh_token="test_refresh_token",
            token_uri="test_token_uri",
            client_id="test_client_id",
            client_secret="test_client_secret",
            scopes="test_scopes",
        )
        test_db.add(test_credentials)
        test_db.flush()
        
        # Create test session with timezone-aware datetime
        session_token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        test_session = DBSession(
            user_id=test_credentials.id, 
            session_token=session_token, 
            expires_at=expires_at
        )
        test_db.add(test_session)
        test_db.commit()
        
        return session_token
    except Exception as e:
        test_db.rollback()
        raise e

# Auth Tests
@patch("main.get_oauth_flow")
def test_auth_login(mock_get_oauth_flow, client):
    # Mock the OAuth flow
    mock_flow = Mock()
    mock_flow.authorization_url.return_value = (
        "https://accounts.google.com/o/oauth2/auth?test=1",
        "test_state"
    )
    mock_get_oauth_flow.return_value = mock_flow

    # Make the request
    response = client.get("/auth/login", follow_redirects=False)

    # Verify response
    assert response.status_code == 307
    assert response.headers["location"] == "https://accounts.google.com/o/oauth2/auth?test=1"

@patch("main.Flow.from_client_config")
def test_auth_callback(mock_flow, client, test_db):
    mock_flow_instance = mock_flow.return_value
    mock_flow_instance.fetch_token.return_value = None
    mock_flow_instance.credentials = Mock(
        token="test_token",
        refresh_token="test_refresh_token",
        token_uri="test_token_uri",
        client_id="test_client_id",
        client_secret="test_client_secret",
        scopes=["test_scope"]
    )
    mock_flow.return_value = mock_flow_instance
    
    response = client.get("/auth/callback?code=testcode&state=teststate")
    assert response.status_code == 200
    assert response.json()["message"] == "Authentication successful"
    assert "session_token" in response.json()

    # Check if credentials and session are stored in the database
    credentials = test_db.query(Credentials).first()
    assert credentials is not None
    assert credentials.token == "test_token"
    
    session = test_db.query(DBSession).first()
    assert session is not None
    assert session.user_id == credentials.id

def test_get_user(client, test_db):
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get("/auth/user", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "test_client_id"

# Search Tests
@patch("main.YTMusic")
def test_search(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.search.return_value = [{"title": "Test Song", "artist": "Test Artist"}]
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/search",
        params={
            "query": "test query",
            "filter": "songs",
            "limit": 20,
            "ignore_spelling": False
        },
        headers=headers
    )
    assert response.status_code == 200
    assert "results" in response.json()

@patch("main.YTMusic")
def test_get_search_suggestions(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_search_suggestions.return_value = ["suggestion1", "suggestion2"]
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/search/suggestions",
        params={"query": "test"},
        headers=headers
    )
    assert response.status_code == 200
    assert "suggestions" in response.json()

@patch("main.YTMusic")
def test_remove_search_suggestions(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.remove_search_suggestions.return_value = None
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.post(
        "/search/suggestions/remove",
        json={"suggestions": [{"text": "test suggestion"}]},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Search suggestions removed successfully"

# Browse Tests
@patch("main.YTMusic")
def test_get_home(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_home.return_value = [{"title": "Home Item"}]
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/browse/home",
        params={"limit": 3},
        headers=headers
    )
    assert response.status_code == 200
    assert "results" in response.json()

@patch("main.YTMusic")
def test_get_artist(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_artist.return_value = {
        "name": "Test Artist",
        "description": "Test Description"
    }
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/browse/artists/test_channel_id",
        headers=headers
    )
    assert response.status_code == 200
    assert "artist" in response.json()

@patch("main.YTMusic")
def test_get_album(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_album.return_value = {
        "title": "Test Album",
        "tracks": [{"title": "Test Track"}]
    }
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/browse/albums/test_browse_id",
        headers=headers
    )
    assert response.status_code == 200
    assert "album" in response.json()

@patch("main.YTMusic")
def test_get_album_browse_id(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_album_browse_id.return_value = "test_browse_id"
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/browse/albums/browse-id/test_video_id",
        headers=headers
    )
    assert response.status_code == 200
    assert "browse_id" in response.json()

@patch("main.YTMusic")
def test_get_user_playlists(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_user.return_value = {
        "name": "Test User",
        "params": "test_params"
    }
    mock_instance.get_user_playlists.return_value = [
        {"title": "User Playlist", "playlistId": "playlist1"}
    ]
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/browse/users/test_channel_id/playlists",
        params={"limit": 25},
        headers=headers
    )
    assert response.status_code == 200
    assert "results" in response.json()

@patch("main.YTMusic")
def test_get_song(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_song.return_value = {
        "videoId": "video1",
        "title": "Test Song",
        "artists": [{"name": "Test Artist"}]
    }
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/browse/songs/video1",
        headers=headers
    )
    assert response.status_code == 200
    assert "song" in response.json()

@patch("main.YTMusic")
def test_get_song_related(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_song_related.return_value = [
        {"videoId": "video2", "title": "Related Song"}
    ]
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/browse/songs/video1/related",
        params={"browse_id": "test_browse_id"},
        headers=headers
    )
    assert response.status_code == 200
    assert "results" in response.json()

# Watch Tests
@patch("main.YTMusic")
def test_get_watch_playlist(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_watch_playlist.return_value = {"tracks": [{"title": "Watch Song"}]}
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/watch/playlist",
        params={"video_id": "test_video_id"},
        headers=headers
    )
    assert response.status_code == 200
    assert "playlist" in response.json()

# Library Tests
@patch("main.YTMusic")
def test_get_library_playlists(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_library_playlists.return_value = [
        {"id": "playlist1", "title": "Test Playlist"}
    ]
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/library/playlists",
        params={"limit": 25},
        headers=headers
    )
    assert response.status_code == 200
    assert "results" in response.json()

@patch("main.YTMusic")
def test_get_liked_songs(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_liked_songs.return_value = {
        "tracks": [{"title": "Liked Song"}],
        "continuation": None
    }
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/library/liked-songs",
        params={"limit": 100},
        headers=headers
    )
    assert response.status_code == 200
    assert "results" in response.json()

# Playlist Tests
@patch("main.YTMusic")
def test_create_playlist(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.create_playlist.return_value = "test_playlist_id"
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.post(
        "/playlists/create",
        params={
            "title": "Test Playlist",
            "description": "Test Description",
            "privacy_status": "PRIVATE",
            "video_ids": ["video1", "video2"]
        },
        headers=headers
    )
    assert response.status_code == 200
    assert "playlist_id" in response.json()

@patch("main.YTMusic")
def test_edit_playlist(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.edit_playlist.return_value = None
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.post(
        "/playlists/test_id/edit",
        json={
            "title": "New Title",
            "description": "New Description",
            "privacy_status": "PRIVATE"
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Playlist edited successfully"

# Upload Tests
@patch("main.YTMusic")
def test_upload_song(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.upload_song.return_value = None
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.post(
        "/uploads/songs",
        params={"filepath": "/path/to/test.mp3"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Song uploaded successfully"

# Podcast Tests
@patch("main.YTMusic")
def test_get_podcast(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_podcast.return_value = {
        "title": "Test Podcast",
        "description": "Test Description",
        "episodes": [{"title": "Test Episode"}]
    }
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/podcasts/test_id",
        headers=headers
    )
    assert response.status_code == 200
    assert "podcast" in response.json()

# Explore Tests
@patch("main.YTMusic")
def test_get_mood_categories(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_mood_categories.return_value = [
        {"title": "Happy", "params": "happy"}
    ]
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/explore/moods",
        headers=headers
    )
    assert response.status_code == 200
    assert "results" in response.json()

@patch("main.YTMusic")
def test_get_mood_playlists(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_mood_playlists.return_value = [
        {"title": "Happy Playlist", "playlistId": "playlist1"}
    ]
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/explore/moods/happy",
        headers=headers
    )
    assert response.status_code == 200
    assert "results" in response.json()
    assert isinstance(response.json()["results"], list)

@patch("main.YTMusic")
def test_get_charts(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_charts.return_value = {
        "countries": ["US"],
        "videos": [{"title": "Top Video"}],
        "artists": [{"name": "Top Artist"}],
        "trending": [{"title": "Trending Video"}]
    }
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/explore/charts/US",
        headers=headers
    )
    assert response.status_code == 200
    assert "results" in response.json()

# Additional Library Tests
@patch("main.YTMusic")
def test_add_history_item(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.add_history_item.return_value = None
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.post(
        "/library/history/add",
        params={"video_id": "test_video_id"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "History item added successfully"

@patch("main.YTMusic")
def test_remove_history_items(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.remove_history_items.return_value = None
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.post(
        "/library/history/remove",
        json={"video_ids": ["test_video_id"]},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "History items removed successfully"

@patch("main.YTMusic")
def test_edit_song_library_status(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.edit_song_library_status.return_value = None
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.post(
        "/library/songs/test_song_id/edit",
        params={"feedback_tokens": ["token1"]},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Song library status updated successfully"

@patch("main.YTMusic")
def test_rate_playlist(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.rate_playlist.return_value = None
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.post(
        "/library/playlists/test_playlist_id/rate",
        json={"rating": "LIKE"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Playlist rated successfully"

# Additional Playlist Tests
@patch("main.YTMusic")
def test_get_playlist(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_playlist.return_value = {
        "title": "Test Playlist",
        "tracks": [{"title": "Test Track"}]
    }
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/playlists/test_playlist_id",
        params={
            "limit": 100,
            "related": False,
            "suggestions_limit": 0
        },
        headers=headers
    )
    assert response.status_code == 200
    assert "playlist" in response.json()

@patch("main.YTMusic")
def test_delete_playlist(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.delete_playlist.return_value = None
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.delete(
        "/playlists/test_playlist_id",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Playlist deleted successfully"

# Additional Upload Tests
@patch("main.YTMusic")
def test_delete_uploaded_song(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.delete_upload_entity.return_value = None
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.delete(
        "/uploads/songs/test_song_id",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Song deleted successfully"

# Additional Podcast Tests
@patch("main.YTMusic")
def test_get_episodes_playlist(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_episodes_playlist.return_value = {
        "title": "Episodes Playlist",
        "episodes": [{"title": "Test Episode"}]
    }
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/podcasts/episodes/playlist/test_episode_id",
        headers=headers
    )
    assert response.status_code == 200
    assert "playlist" in response.json()

@patch("main.YTMusic")
def test_get_episode(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_episode.return_value = {
        "title": "Test Episode",
        "description": "Test Description",
        "duration": "10:00"
    }
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/podcasts/episodes/test_episode_id",
        headers=headers
    )
    assert response.status_code == 200
    assert "episode" in response.json()

@patch("main.YTMusic")
def test_get_library_podcasts(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_library_podcasts.return_value = [
        {"title": "Library Podcast", "description": "Test Description"}
    ]
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/library/podcasts",
        params={"limit": 25},
        headers=headers
    )
    assert response.status_code == 200
    assert "results" in response.json()

@patch("main.YTMusic")
def test_get_library_channels(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_library_channels.return_value = [
        {"name": "Test Channel", "channelId": "channel1"}
    ]
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/library/channels",
        params={"limit": 25},
        headers=headers
    )
    assert response.status_code == 200
    assert "results" in response.json()

@patch("main.YTMusic")
def test_get_saved_episodes(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_saved_episodes.return_value = [
        {"title": "Saved Episode", "episodeId": "episode1"}
    ]
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/library/episodes",
        params={"limit": 25},
        headers=headers
    )
    assert response.status_code == 200
    assert "results" in response.json()

@patch("main.YTMusic")
def test_get_library_upload_artist(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_library_upload_artist.return_value = {
        "name": "Test Artist",
        "songs": [{"title": "Test Song"}]
    }
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/uploads/artists/test_artist_id",
        headers=headers
    )
    assert response.status_code == 200
    assert "artist" in response.json()

@patch("main.YTMusic")
def test_get_library_upload_album(mock_ytmusic, client, test_db):
    mock_instance = Mock()
    mock_instance.get_library_upload_album.return_value = {
        "title": "Test Album",
        "tracks": [{"title": "Test Track"}]
    }
    mock_ytmusic.return_value = mock_instance
    
    session_token = create_test_session(test_db)
    headers = {"Authorization": f"Bearer {session_token}"}
    response = client.get(
        "/uploads/albums/test_album_id",
        headers=headers
    )
    assert response.status_code == 200
    assert "album" in response.json()
