from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from app.core.security import get_current_user
from app.schemas.models import CredentialsModel
from app.services.ytmusic import YTMusicService, LibraryOrderType

router = APIRouter()

@router.get("/channel/{channel_id}")
async def get_channel(
    channel_id: str,
    credentials: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get information about a podcast channel."""
    ytmusic = YTMusicService(credentials)
    return ytmusic.get_channel(channel_id=channel_id)

@router.get("/channel/{channel_id}/episodes")
async def get_channel_episodes(
    channel_id: str,
    params: str,
    credentials: CredentialsModel = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get all episodes from a podcast channel."""
    ytmusic = YTMusicService(credentials)
    return ytmusic.get_channel_episodes(channel_id=channel_id, params=params)

@router.get("/podcast/{playlist_id}")
async def get_podcast(
    playlist_id: str,
    limit: Optional[int] = 100,
    credentials: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get podcast metadata and episodes."""
    ytmusic = YTMusicService(credentials)
    return ytmusic.get_podcast(playlist_id=playlist_id, limit=limit)

@router.get("/episode/{video_id}")
async def get_episode(
    video_id: str,
    credentials: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get episode data for a single episode."""
    ytmusic = YTMusicService(credentials)
    return ytmusic.get_episode(video_id=video_id)

@router.get("/episodes/playlist/{playlist_id}")
async def get_episodes_playlist(
    playlist_id: str = "RDPN",
    credentials: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get all episodes in an episodes playlist."""
    ytmusic = YTMusicService(credentials)
    return ytmusic.get_episodes_playlist(playlist_id=playlist_id)

@router.get("/library")
async def get_library_podcasts(
    limit: int = 25,
    order: Optional[LibraryOrderType] = None,
    credentials: CredentialsModel = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get podcasts the user has added to the library."""
    ytmusic = YTMusicService(credentials)
    return ytmusic.get_library_podcasts(limit=limit, order=order)

@router.get("/saved-episodes")
async def get_saved_episodes(
    limit: int = 100,
    credentials: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get playlist items for the 'Saved Episodes' playlist."""
    ytmusic = YTMusicService(credentials)
    return ytmusic.get_saved_episodes(limit=limit) 
