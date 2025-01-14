from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from app.core.security import get_current_user
from app.schemas.models import (
    CredentialsModel,
    SearchResults,
    WatchPlaylistResponse,
    MessageResponse
)
from app.services.ytmusic import YTMusicService, ArtistOrderType

router = APIRouter()

@router.get("/home", response_model=SearchResults)
async def get_home(
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get home page content."""
    try:
        ytmusic = YTMusicService(current_user)
        results = ytmusic.get_home()
        if isinstance(results, list):
            return {"results": results}
        if isinstance(results, dict):
            return {"results": results}
        return {"results": []}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/artists/{channel_id}", response_model=Dict[str, Dict[str, Any]])
async def get_artist(
    channel_id: str = "",
    browse_id: Optional[str] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get artist details."""
    ytmusic = YTMusicService(current_user)
    artist = ytmusic.get_artist(channel_id=channel_id, browse_id=browse_id)
    return {"artist": artist}

@router.get("/artists/{channel_id}/albums", response_model=Dict[str, Dict[str, Any]])
async def get_artist_albums(
    channel_id: str,
    limit: Optional[int] = None,
    order: Optional[ArtistOrderType] = None,
    params: str = "",
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get artist's albums."""
    ytmusic = YTMusicService(current_user)
    albums = ytmusic.get_artist_albums(
        channel_id=channel_id,
        limit=limit,
        order=order,
        params=params
    )
    return {"albums": albums}

@router.get("/albums/{browse_id}", response_model=Dict[str, Dict[str, Any]])
async def get_album(
    browse_id: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get album details."""
    ytmusic = YTMusicService(current_user)
    album = ytmusic.get_album(browse_id)
    return {"album": album}

@router.get("/albums/browse/{audio_playlist_id}", response_model=Dict[str, str])
async def get_album_browse_id(
    audio_playlist_id: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Get album browse ID from audio playlist ID."""
    ytmusic = YTMusicService(current_user)
    browse_id = ytmusic.get_album_browse_id(audio_playlist_id)
    return {"browse_id": browse_id or ""}

@router.get("/users/{channel_id}", response_model=Dict[str, Dict[str, Any]])
async def get_user(
    channel_id: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get user details."""
    ytmusic = YTMusicService(current_user)
    user = ytmusic.get_user(channel_id)
    return {"user": user}

@router.get("/users/{channel_id}/playlists", response_model=SearchResults)
async def get_user_playlists(
    channel_id: str,
    params: Optional[str] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get user's playlists."""
    ytmusic = YTMusicService(current_user)
    playlists = ytmusic.get_user_playlists(channel_id=channel_id, params=params)
    return {"results": playlists}

@router.get("/users/{channel_id}/videos", response_model=SearchResults)
async def get_user_videos(
    channel_id: str,
    params: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get user's videos."""
    ytmusic = YTMusicService(current_user)
    videos = ytmusic.get_user_videos(channel_id=channel_id, params=params)
    return {"results": videos}

@router.get("/playlists/{playlist_id}", response_model=WatchPlaylistResponse)
async def get_playlist(
    playlist_id: str,
    limit: Optional[int] = 100,
    related: bool = False,
    suggestions_limit: int = 0,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get playlist details."""
    ytmusic = YTMusicService(current_user)
    playlist = ytmusic.get_playlist(
        playlist_id=playlist_id,
        limit=limit,
        related=related,
        suggestions_limit=suggestions_limit
    )
    return {"playlist": playlist}

@router.get("/songs/{video_id}", response_model=Dict[str, Dict[str, Any]])
async def get_song(
    video_id: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get song details."""
    ytmusic = YTMusicService(current_user)
    song = ytmusic.get_song(video_id=video_id)
    return {"song": song}

@router.get("/songs/{browse_id}/related", response_model=Dict[str, Dict[str, Any]])
async def get_song_related(
    browse_id: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get related songs."""
    ytmusic = YTMusicService(current_user)
    related = ytmusic.get_song_related(browse_id)
    return {"related": related}

@router.get("/tasteprofile", response_model=Dict[str, Dict[str, Any]])
async def get_tasteprofile(
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get your taste profile."""
    ytmusic = YTMusicService(current_user)
    profile = ytmusic.get_tasteprofile()
    return {"profile": profile}

@router.post("/tasteprofile", response_model=MessageResponse)
async def set_tasteprofile(
    artists: List[str],
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Set your taste profile."""
    ytmusic = YTMusicService(current_user)
    success = ytmusic.set_tasteprofile(artists)
    return {"message": "Taste profile updated successfully" if success else "Failed to update taste profile"} 
