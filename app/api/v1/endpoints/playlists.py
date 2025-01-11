from fastapi import APIRouter, Depends, Body
from typing import Optional, List, Dict, Any, Union, Tuple
from app.core.security import get_current_user
from app.schemas.models import (
    CredentialsModel,
    PlaylistResponse,
    MessageResponse,
    WatchPlaylistResponse,
    PrivacyStatus
)
from app.services.ytmusic import YTMusicService

router = APIRouter()

@router.get("/{playlist_id}", response_model=WatchPlaylistResponse)
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

@router.post("/create", response_model=PlaylistResponse)
async def create_playlist(
    title: str = Body(...),
    description: str = Body(""),
    privacy_status: PrivacyStatus = Body(PrivacyStatus.PRIVATE),
    video_ids: Optional[List[str]] = Body(None),
    source_playlist: Optional[str] = Body(None),
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Create a new playlist."""
    ytmusic = YTMusicService(current_user)
    result = ytmusic.create_playlist(
        title=title,
        description=description,
        privacy_status=privacy_status.value,
        video_ids=video_ids,
        source_playlist=source_playlist
    )
    if isinstance(result, str):
        return {"playlist_id": result}
    return {"playlist_id": result.get("playlistId", "")}

@router.post("/{playlist_id}/edit", response_model=MessageResponse)
async def edit_playlist(
    playlist_id: str,
    title: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    privacy_status: Optional[PrivacyStatus] = Body(None),
    move_item: Optional[Union[str, Tuple[str, str]]] = Body(None),
    add_playlist_id: Optional[str] = Body(None),
    add_to_top: Optional[bool] = Body(None),
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Edit playlist details."""
    ytmusic = YTMusicService(current_user)
    result = ytmusic.edit_playlist(
        playlist_id=playlist_id,
        title=title,
        description=description,
        privacy_status=privacy_status.value if privacy_status else None,
        move_item=move_item,
        add_playlist_id=add_playlist_id,
        add_to_top=add_to_top
    )
    if isinstance(result, str):
        return {"message": result}
    return {"message": "Playlist updated successfully"}

@router.post("/{playlist_id}/items", response_model=MessageResponse)
async def add_playlist_items(
    playlist_id: str,
    video_ids: List[str] = Body(..., embed=True),
    source_playlist: Optional[str] = Body(None),
    duplicates: bool = Body(False),
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Add items to playlist."""
    ytmusic = YTMusicService(current_user)
    result = ytmusic.add_playlist_items(
        playlist_id=playlist_id,
        video_ids=video_ids,
        source_playlist=source_playlist,
        duplicates=duplicates
    )
    if isinstance(result, str):
        return {"message": result}
    return {"message": "Items added to playlist successfully"}

@router.delete("/{playlist_id}/items", response_model=MessageResponse)
async def remove_playlist_items(
    playlist_id: str,
    videos: List[Dict[str, Any]] = Body(..., embed=True),
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Remove items from playlist.
    
    The videos parameter should be a list of dictionaries containing setVideoId.
    Example: [{"setVideoId": "video_id_1"}, {"setVideoId": "video_id_2"}]
    """
    ytmusic = YTMusicService(current_user)
    result = ytmusic.remove_playlist_items(playlist_id=playlist_id, videos=videos)
    if isinstance(result, str):
        return {"message": result}
    return {"message": "Items removed from playlist successfully"}

@router.delete("/{playlist_id}", response_model=MessageResponse)
async def delete_playlist(
    playlist_id: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete a playlist."""
    ytmusic = YTMusicService(current_user)
    result = ytmusic.delete_playlist(playlist_id)
    if isinstance(result, str):
        return {"message": result}
    return {"message": "Playlist deleted successfully"} 
