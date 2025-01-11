from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class PrivacyStatus(str, Enum):
    PUBLIC = "PUBLIC"
    UNLISTED = "UNLISTED"
    PRIVATE = "PRIVATE"

class CredentialsModel(BaseModel):
    token: str
    refresh_token: Optional[str] = None
    token_uri: str
    client_id: str
    client_secret: str
    scopes: Optional[List[str]] = None

class MessageResponse(BaseModel):
    message: str

class AuthResponse(BaseModel):
    url: str

class SearchResults(BaseModel):
    results: Union[List[Dict[str, Any]], Dict[str, Any], List[str], List[Any]]

class SearchSuggestionsResponse(BaseModel):
    suggestions: List[Union[str, Dict[str, Any]]]

class SearchSuggestionsRequest(BaseModel):
    suggestions: List[Dict[str, str]]

class PlaylistResponse(BaseModel):
    playlist_id: str

class WatchPlaylistResponse(BaseModel):
    playlist: Dict[str, Any]

class LyricsResponse(BaseModel):
    lyrics: Dict[str, Any]

class PodcastResponse(BaseModel):
    podcast: Dict[str, Any]

class EpisodeResponse(BaseModel):
    episode: Dict[str, Any]

class EpisodesPlaylistResponse(BaseModel):
    episodes: List[Dict[str, Any]]

class HistoryItemsRequest(BaseModel):
    video_ids: List[str]

class UploadArtistResponse(BaseModel):
    artist: Dict[str, Any]

class UploadAlbumResponse(BaseModel):
    album: Dict[str, Any] 
