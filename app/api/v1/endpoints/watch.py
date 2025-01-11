from fastapi import APIRouter, Depends
from typing import Optional, Dict, Any
from app.core.security import get_current_user
from app.schemas.models import (
    CredentialsModel,
    WatchPlaylistResponse,
    LyricsResponse
)
from app.services.ytmusic import YTMusicService

router = APIRouter()

@router.get("/playlist", response_model=WatchPlaylistResponse)
async def get_watch_playlist(
    video_id: Optional[str] = None,
    playlist_id: Optional[str] = None,
    limit: int = 25,
    radio: bool = False,
    shuffle: bool = False,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get watch playlist."""
    ytmusic = YTMusicService(current_user)
    playlist = ytmusic.get_watch_playlist(
        video_id=video_id,
        playlist_id=playlist_id,
        limit=limit,
        radio=radio,
        shuffle=shuffle
    )
    return {"playlist": playlist}

@router.get("/lyrics/{browse_id}", response_model=LyricsResponse)
async def get_lyrics(
    browse_id: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get song lyrics."""
    ytmusic = YTMusicService(current_user)
    lyrics = ytmusic.get_lyrics(browse_id)
    return {"lyrics": lyrics} 
