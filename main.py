from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google_auth_oauthlib.flow import Flow
import os
from sqlalchemy.orm import Session
from database import SessionLocal, Credentials, create_db_and_tables, Session as DBSession
from datetime import datetime, timedelta, timezone
import uuid
from typing import Annotated, List, Optional, Dict, Any, cast
from ytmusicapi import YTMusic
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from models import CredentialsModel
from enum import Enum

load_dotenv()

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")

# Debug prints
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
if DEBUG:
    print("Environment variables loaded:")
    print(f"GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID[:10]}..." if GOOGLE_CLIENT_ID else "Not set")
    print(f"GOOGLE_CLIENT_SECRET: {GOOGLE_CLIENT_SECRET[:5]}..." if GOOGLE_CLIENT_SECRET else "Not set")
    print(f"GOOGLE_REDIRECT_URI: {GOOGLE_REDIRECT_URI}" if GOOGLE_REDIRECT_URI else "Not set")

# Environment variable validation
if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI]):
    raise ValueError("Missing required environment variables")

# Response models
class PlaylistResponse(BaseModel):
    playlist_id: str

class MessageResponse(BaseModel):
    message: str

class SearchResults(BaseModel):
    results: List[Dict[str, Any]]

class WatchPlaylistResponse(BaseModel):
    playlist: Dict[str, Any]

class ArtistResponse(BaseModel):
    artist: Dict[str, Any]

class AlbumResponse(BaseModel):
    album: Dict[str, Any]

class LyricsResponse(BaseModel):
    lyrics: Dict[str, Any]

class SubscriptionResponse(BaseModel):
    status: bool = False

class RatingResponse(BaseModel):
    status: str

class SearchSuggestionsResponse(BaseModel):
    suggestions: List[str]

class BrowseIDResponse(BaseModel):
    browse_id: str

class SongResponse(BaseModel):
    song: Dict[str, Any]

class PodcastResponse(BaseModel):
    podcast: Dict[str, Any]

class EpisodeResponse(BaseModel):
    episode: Dict[str, Any]

class EpisodesPlaylistResponse(BaseModel):
    playlist: Dict[str, Any]

class UploadArtistResponse(BaseModel):
    artist: Dict[str, Any]

class UploadAlbumResponse(BaseModel):
    album: Dict[str, Any]

class LibraryOrderType(str, Enum):
    A_TO_Z = "a_to_z"
    Z_TO_A = "z_to_a"
    RECENTLY_ADDED = "recently_added"

class PrivacyStatus(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
    UNLISTED = "UNLISTED"

class SearchFilter(str, Enum):
    SONGS = "songs"
    VIDEOS = "videos"
    ALBUMS = "albums"
    ARTISTS = "artists"
    PLAYLISTS = "playlists"
    COMMUNITY_PLAYLISTS = "community_playlists"
    FEATURED_PLAYLISTS = "featured_playlists"
    UPLOADS = "uploads"

class SearchScope(str, Enum):
    LIBRARY = "library"
    UPLOADS = "uploads"

class ArtistParamsFilter(str, Enum):
    ALBUMS = "albums"
    SINGLES = "singles"
    VIDEOS = "videos"
    COMMUNITY = "community"

class HistoryItemsRequest(BaseModel):
    video_ids: List[str]

class SearchSuggestion(BaseModel):
    text: str

class SearchSuggestionsRequest(BaseModel):
    suggestions: List[SearchSuggestion]

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# Dependency to get the database session
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

# Dependency to validate session
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> CredentialsModel:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        scheme, session_token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db_session = db.query(DBSession).filter(DBSession.session_token == session_token).first()

    if not db_session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    current_time = datetime.now(timezone.utc)
    if db_session.expires_at.replace(tzinfo=timezone.utc) < current_time:
        raise HTTPException(status_code=401, detail="Session expired")
    
    user = db.query(Credentials).filter(Credentials.id == db_session.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_dict = {
        "id": user.id,
        "token": user.token,
        "refresh_token": user.refresh_token,
        "token_uri": user.token_uri,
        "client_id": user.client_id,
        "client_secret": user.client_secret,
        "scopes": user.scopes.split(",") if user.scopes is not None else []
    }
    
    return CredentialsModel.model_validate(user_dict)

def create_oauth_dict(credentials: CredentialsModel) -> dict:
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes if credentials.scopes else []
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

    with SessionLocal() as db:
        db.query(DBSession).filter(DBSession.expires_at < datetime.utcnow()).delete()
        db.commit()

# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

# OAuth helper function
def get_oauth_flow():
    flow = Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    return flow

# Auth Endpoints
@app.get("/auth/login")
async def login():
    """
    Redirect to Google OAuth login page
    """
    flow = get_oauth_flow()
    
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    
    if DEBUG:
        print(f"Authorization URL: {authorization_url}")
        print(f"State: {state}")
        print(f"Redirect URI: {GOOGLE_REDIRECT_URI}")

    return RedirectResponse(
        url=authorization_url,
        status_code=307
    )

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/auth/callback")
async def auth_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None
):
    """
    Handle the OAuth callback from Google
    """
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided")
    
    try:
        flow = get_oauth_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Store credentials in database
        db = next(get_db())
        db_credentials = Credentials(
            token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri, # type: ignore
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            scopes=",".join(credentials.scopes) if credentials.scopes else ""
        )
        db.add(db_credentials)
        db.commit()
        
        # Create session
        session_token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        db_session = DBSession(
            user_id=db_credentials.id,
            session_token=session_token,
            expires_at=expires_at
        )
        db.add(db_session)
        db.commit()
        
        return {"message": "Authentication successful", "session_token": session_token}
        
    except Exception as e:
        print(f"Error in callback: {str(e)}")  # Debug print
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch token: {str(e)}"
        )

@app.get("/auth/user")
async def get_user(current_user: Annotated[CredentialsModel, Depends(get_current_user)]):
    return {"username": current_user.client_id}

# Search Endpoints
@app.get("/search", response_model=SearchResults)
async def search(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    query: str,
    filter: Optional[SearchFilter] = None,
    scope: Optional[SearchScope] = None,
    limit: int = 20,
    ignore_spelling: bool = False
):
    """
    Search on YouTube Music.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        results = ytmusic.search(
            query=query, 
            filter=filter.value if filter else None,
            scope=scope.value if scope else None,
            limit=limit,
            ignore_spelling=ignore_spelling
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/search/suggestions", response_model=SearchSuggestionsResponse)
async def get_search_suggestions(
    query: str,
    current_user: Annotated[CredentialsModel, Depends(get_current_user)]
):
    """
    Get search suggestions for the given query.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        suggestions = ytmusic.get_search_suggestions(query)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/search/suggestions/remove", response_model=MessageResponse)
async def remove_search_suggestions(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    request: SearchSuggestionsRequest
):
    """
    Remove search suggestions
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        suggestions = [{"text": s.text} for s in request.suggestions]
        ytmusic.remove_search_suggestions(suggestions)
        return {"message": "Search suggestions removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Browse Endpoints
@app.get("/browse/home", response_model=SearchResults)
async def get_home(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 3,
):
    """
    Get the home feed content.
    continuation token can be used to get more results.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        home = ytmusic.get_home(limit=limit)
        return {"results": home}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/browse/artists/{channel_id}", response_model=ArtistResponse)
async def get_artist(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    channel_id: str,
):
    """
    Get artist information and songs.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        artist = ytmusic.get_artist(channelId=channel_id)
        return {"artist": artist}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/browse/artists/{artist_id}/albums", response_model=SearchResults)
async def get_artist_albums(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    artist_id: str,
    params: ArtistParamsFilter = ArtistParamsFilter.ALBUMS,
    limit: int = 25
):
    """
    Get artist's albums.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        albums = ytmusic.get_artist_albums(
            channelId=artist_id, 
            params=params.value,
            limit=limit
        )
        return {"results": albums}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/browse/albums/{browse_id}", response_model=AlbumResponse)
async def get_album(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    browse_id: str,
):
    """
    Get information and tracks of an album.
    If download_urls=True, download URLs will be included (requires authentication).
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        album = ytmusic.get_album(browseId=browse_id)
        return {"album": album}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/browse/albums/browse-id/{video_id}", response_model=BrowseIDResponse)
async def get_album_browse_id(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    video_id: str
):
    """
    Get an album's browse id from a track video id
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        browse_id = ytmusic.get_album_browse_id(video_id)
        return {"browse_id": browse_id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/browse/users/{channel_id}", response_model=SearchResults)
async def get_user_info(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    channel_id: str
):
    """
    Get a user's information
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        user = ytmusic.get_user(channelId=channel_id)
        return {"results": user}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/browse/users/{channel_id}/playlists", response_model=SearchResults)
async def get_user_playlists(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    channel_id: str
):
    """
    Get a user's playlists
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        user = ytmusic.get_user(channelId=channel_id)
        playlists = ytmusic.get_user_playlists(channelId=channel_id, params=user['params'])
        return {"results": playlists}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/browse/songs/{video_id}", response_model=SongResponse)
async def get_song(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    video_id: str
):
    """
    Get song metadata
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        song = ytmusic.get_song(videoId=video_id)
        return {"song": song}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/browse/songs/{video_id}/related", response_model=SearchResults)
async def get_song_related(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    browse_id: str
):
    """
    Get related songs
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        related = ytmusic.get_song_related(browseId=browse_id)
        return {"results": related}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Explore Endpoints
@app.get("/explore/moods", response_model=SearchResults)
async def get_mood_categories(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)]
):
    """
    Get mood categories.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        moods = ytmusic.get_mood_categories()
        return {"results": moods}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/explore/moods/{params}", response_model=SearchResults)
async def get_mood_playlists(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    params: str
):
    """
    Get playlists for a specific mood category.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        playlists = ytmusic.get_mood_playlists(params)
        if not isinstance(playlists, list):
            playlists = [playlists]
        return {"results": playlists}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/explore/charts/{country_code}", response_model=SearchResults)
async def get_charts(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    country_code: str = "ZZ"
):
    """
    Get charts data from YouTube Music.
    country_code: ISO 3166-1 Alpha-2 country code. Default: ZZ = Global
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        charts = ytmusic.get_charts(country=country_code)
        # Convert charts to a list format for SearchResults model
        results = []
        for category in ["videos", "artists", "trending"]:
            if category in charts:
                results.extend(charts[category])
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Watch Endpoints
@app.get("/watch/playlist", response_model=WatchPlaylistResponse)
async def get_watch_playlist(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    video_id: Optional[str] = None,
    playlist_id: Optional[str] = None,
    limit: int = 25,
    radio: bool = False,
    shuffle: bool = False
):
    """
    Get a watch playlist. Can be created from a video_id or playlist_id.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        playlist = ytmusic.get_watch_playlist(
            videoId=video_id,
            playlistId=playlist_id,
            limit=limit,
            radio=radio,
            shuffle=shuffle
        )
        return {"playlist": playlist}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/watch/lyrics/{browse_id}", response_model=LyricsResponse)
async def get_lyrics(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    browse_id: str
):
    """
    Get lyrics for a song.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        lyrics = ytmusic.get_lyrics(browse_id)
        return {"lyrics": lyrics}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Library Endpoints
@app.get("/library/playlists", response_model=SearchResults)
async def get_library_playlists(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 25
):
    """
    Retrieves the playlists in the user's library.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        playlists = ytmusic.get_library_playlists(limit=limit)
        return {"results": playlists}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/library/songs", response_model=SearchResults)
async def get_library_songs(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 25,
    order: Optional[LibraryOrderType] = None
):
    """
    Get songs in the user's library.
    order options: recently_added, recently_played, a_to_z, z_to_a
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        library = ytmusic.get_library_songs(
            limit=limit,
            order=order.value if order else None
        )
        return {"results": library}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/library/albums", response_model=SearchResults)
async def get_library_albums(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 25
):
    """
    Get the albums in the user's library.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        albums = ytmusic.get_library_albums(limit=limit)
        return {"results": albums}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/library/artists", response_model=SearchResults)
async def get_library_artists(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 25
):
    """
    Get the artists in the user's library.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        artists = ytmusic.get_library_artists(limit=limit)
        return {"results": artists}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/library/subscriptions", response_model=SearchResults)
async def get_library_subscriptions(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 25
):
    """
    Get the artists the user is subscribed to.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        subscriptions = ytmusic.get_library_subscriptions(limit=limit)
        return {"results": subscriptions}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/library/liked-songs", response_model=SearchResults)
async def get_liked_songs(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 100
):
    """
    Gets playlist items for the 'Liked Songs' playlist
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        songs = ytmusic.get_liked_songs(limit=limit)
        return {"results": songs["tracks"]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/library/history", response_model=SearchResults)
async def get_history(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)]
):
    """
    Get the user's listening history.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        history = ytmusic.get_history()
        return {"results": history}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/library/history/add", response_model=MessageResponse)
async def add_history_item(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    video_id: str
):
    """
    Add a video to history
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        ytmusic.add_history_item(song=video_id)
        return {"message": "History item added successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/library/history/remove", response_model=MessageResponse)
async def remove_history_items(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    request: HistoryItemsRequest
):
    """
    Remove videos from history
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        ytmusic.remove_history_items(request.video_ids)
        return {"message": "History items removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Playlist Endpoints
@app.get("/playlists/{playlist_id}", response_model=WatchPlaylistResponse)
async def get_playlist(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    playlist_id: str,
    limit: Optional[int] = 100,
    related: bool = False,
    suggestions_limit: int = 0
):
    """
    Get a playlist's information and tracks.
    If related=True, related songs will be returned.
    suggestions_limit sets the number of suggested songs to return
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        playlist = ytmusic.get_playlist(
            playlistId=playlist_id,
            limit=limit,
            related=related,
            suggestions_limit=suggestions_limit
        )
        return {"playlist": playlist}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/playlists/create", response_model=PlaylistResponse)
async def create_playlist(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    title: str,
    description: str = "",
    privacy_status: PrivacyStatus = PrivacyStatus.PRIVATE,
    video_ids: Optional[List[str]] = None,
    source_playlist: Optional[str] = None
):
    """
    Create a new playlist.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        playlist_id = ytmusic.create_playlist(
            title=title,
            description=description,
            privacy_status=privacy_status.value,
            video_ids=video_ids,
            source_playlist=source_playlist
        )
        return {"playlist_id": playlist_id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/playlists/{playlist_id}/edit", response_model=MessageResponse)
async def edit_playlist(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    playlist_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    privacy_status: Optional[str] = None,
    move_item: Optional[str] = None,
    add_playlist_id: Optional[str] = None,
    add_to_top: Optional[bool] = None,
):
    """
    Edit a playlist's details and contents.
    privacy_status options: PRIVATE, PUBLIC, UNLISTED
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        ytmusic.edit_playlist(
            playlistId=playlist_id,
            title=title,
            description=description,
            privacyStatus=privacy_status,
            moveItem=move_item,
            addPlaylistId=add_playlist_id,
            addToTop=add_to_top
        )
        return {"message": "Playlist edited successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.delete("/playlists/{playlist_id}", response_model=MessageResponse)
async def delete_playlist(
    playlist_id: str,
    current_user: Annotated[CredentialsModel, Depends(get_current_user)]
):
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        ytmusic.delete_playlist(playlist_id)

        return {"message": "Playlist deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Upload Endpoints
@app.post("/uploads/songs", response_model=MessageResponse)
async def upload_song(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    filepath: str
):
    """
    Upload a song to YouTube Music.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        ytmusic.upload_song(filepath)
        return {"message": "Song uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.delete("/uploads/songs/{song_id}", response_model=MessageResponse)
async def delete_uploaded_song(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    song_id: str
):
    """
    Delete an uploaded song from YouTube Music.
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        ytmusic.delete_upload_entity(song_id)
        return {"message": "Song deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/uploads/songs", response_model=SearchResults)
async def get_library_upload_songs(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 25
):
    """
    Get uploaded songs
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        songs = ytmusic.get_library_upload_songs(limit=limit)
        return {"results": songs}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/uploads/artists", response_model=SearchResults)
async def get_library_upload_artists(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 25
):
    """
    Get uploaded artists
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        artists = ytmusic.get_library_upload_artists(limit=limit)
        return {"results": artists}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/uploads/albums", response_model=SearchResults)
async def get_library_upload_albums(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 25
):
    """
    Get uploaded albums
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        albums = ytmusic.get_library_upload_albums(limit=limit)
        return {"results": albums}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Podcast Endpoints
@app.get("/podcasts/channels/{channel_id}", response_model=SearchResults)
async def get_podcast_channel(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    channel_id: str
):
    """
    Get podcast channel information
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        channel = ytmusic.get_channel(channelId=channel_id)
        return {"results": channel}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/podcasts/channels/{channel_id}/episodes", response_model=SearchResults)
async def get_podcast_episodes(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    channel_id: str
):
    """
    Get podcast channel episodes
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        episodes = ytmusic.get_channel_episodes(channelId=channel_id, params=channel_id)
        return {"results": episodes}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Add to Browse Endpoints
@app.get("/browse/users/{channel_id}/videos", response_model=SearchResults)
async def get_user_videos(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    channel_id: str
):
    """
    Get a user's uploaded videos
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        videos = ytmusic.get_user_videos(channelId=channel_id, params=channel_id)
        return {"results": videos}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/browse/tasteprofile", response_model=SearchResults)
async def get_tasteprofile(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)]
):
    """
    Get user's taste profile
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        profile = ytmusic.get_tasteprofile()
        return {"results": profile}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/browse/tasteprofile", response_model=MessageResponse)
async def set_tasteprofile(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    artists: List[str]
):
    """
    Set user's taste profile
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        ytmusic.set_tasteprofile(artists)
        return {"message": "Taste profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Add to Library Endpoints
@app.get("/library/podcasts", response_model=SearchResults)
async def get_library_podcasts(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 25
):
    """
    Get podcasts in user's library
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        podcasts = ytmusic.get_library_podcasts(limit=limit)
        return {"results": podcasts}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/library/channels", response_model=SearchResults)
async def get_library_channels(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 25
):
    """
    Get channels in user's library
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        channels = ytmusic.get_library_channels(limit=limit)
        return {"results": channels}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/library/episodes", response_model=SearchResults)
async def get_saved_episodes(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    limit: int = 25
):
    """
    Get saved podcast episodes
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        episodes = ytmusic.get_saved_episodes(limit=limit)
        return {"results": episodes}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/library/songs/{song_id}/edit", response_model=MessageResponse)
async def edit_song_library_status(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    song_id: str,
    feedback_tokens: Optional[List[str]] = None
):
    """
    Edit a song's library status using feedback tokens
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        ytmusic.edit_song_library_status(feedbackTokens=feedback_tokens)
        return {"message": "Song library status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/library/playlists/{playlist_id}/rate", response_model=MessageResponse)
async def rate_playlist(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    playlist_id: str,
    rating: str = "INDIFFERENT"
):
    """
    Rate a playlist ("LIKE", "DISLIKE", "INDIFFERENT")
    """
    if rating not in ["LIKE", "DISLIKE", "INDIFFERENT"]:
        raise HTTPException(status_code=400, detail="Invalid rating value")

    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        ytmusic.rate_playlist(playlistId=playlist_id, rating=rating)
        return {"message": "Playlist rated successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/library/account", response_model=SearchResults)
async def get_account_info(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)]
):
    """
    Get account info
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        info = ytmusic.get_account_info()
        return {"results": info}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Add to Podcast Endpoints
@app.get("/podcasts/{podcast_id}", response_model=PodcastResponse)
async def get_podcast(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    podcast_id: str
):
    """
    Get podcast information
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        podcast = ytmusic.get_podcast(podcast_id)
        return {"podcast": podcast}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/podcasts/episodes/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    episode_id: str
):
    """
    Get podcast episode information
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        episode = ytmusic.get_episode(episode_id)
        return {"episode": episode}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/podcasts/episodes/playlist/{episode_id}", response_model=EpisodesPlaylistResponse)
async def get_episodes_playlist(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    episode_id: str
):
    """
    Get podcast episode playlist
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        playlist = ytmusic.get_episodes_playlist(episode_id)
        return {"playlist": playlist}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Add to Upload Endpoints
@app.get("/uploads/artists/{artist_id}", response_model=UploadArtistResponse)
async def get_library_upload_artist(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    artist_id: str
):
    """
    Get uploaded artist information
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        artist = ytmusic.get_library_upload_artist(artist_id)
        return {"artist": artist}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/uploads/albums/{album_id}", response_model=UploadAlbumResponse)
async def get_library_upload_album(
    current_user: Annotated[CredentialsModel, Depends(get_current_user)],
    album_id: str
):
    """
    Get uploaded album information
    """
    oauth = create_oauth_dict(current_user)
    ytmusic = YTMusic(auth=oauth)

    try:
        album = ytmusic.get_library_upload_album(album_id)
        return {"album": album}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
