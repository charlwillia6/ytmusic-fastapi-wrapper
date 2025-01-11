from fastapi import APIRouter, Depends, Body
from typing import Dict, Any, List, Optional
from app.core.security import get_current_user
from app.schemas.models import CredentialsModel, SearchResults, MessageResponse
from app.services.ytmusic import YTMusicService, LibraryOrderType

router = APIRouter()

@router.get("/playlists", response_model=SearchResults)
async def get_library_playlists(
    limit: Optional[int] = 25,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get library playlists."""
    ytmusic = YTMusicService(current_user)
    results = ytmusic.get_library_playlists(limit=limit)
    return {"results": results}

@router.get("/songs", response_model=SearchResults)
async def get_library_songs(
    limit: int = 25,
    validate_responses: bool = False,
    order: Optional[LibraryOrderType] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get library songs."""
    ytmusic = YTMusicService(current_user)
    results = ytmusic.get_library_songs(
        limit=limit,
        validate_responses=validate_responses,
        order=order
    )
    return {"results": results}

@router.get("/albums", response_model=SearchResults)
async def get_library_albums(
    limit: int = 25,
    order: Optional[LibraryOrderType] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get library albums."""
    ytmusic = YTMusicService(current_user)
    results = ytmusic.get_library_albums(limit=limit, order=order)
    return {"results": results}

@router.get("/artists", response_model=SearchResults)
async def get_library_artists(
    limit: int = 25,
    order: Optional[LibraryOrderType] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get library artists."""
    ytmusic = YTMusicService(current_user)
    results = ytmusic.get_library_artists(limit=limit, order=order)
    return {"results": results}

@router.get("/subscriptions", response_model=SearchResults)
async def get_library_subscriptions(
    limit: int = 25,
    order: Optional[LibraryOrderType] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get library subscriptions."""
    ytmusic = YTMusicService(current_user)
    results = ytmusic.get_library_subscriptions(limit=limit, order=order)
    return {"results": results}

@router.get("/channels", response_model=SearchResults)
async def get_library_channels(
    limit: int = 25,
    order: Optional[LibraryOrderType] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get channels the user has added to the library."""
    ytmusic = YTMusicService(current_user)
    results = ytmusic.get_library_channels(limit=limit, order=order)
    return {"results": results}

@router.get("/liked", response_model=SearchResults)
async def get_liked_songs(
    limit: int = 100,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get liked songs."""
    ytmusic = YTMusicService(current_user)
    results = ytmusic.get_liked_songs(limit=limit)
    return {"results": results.get("tracks", [])}

@router.get("/history", response_model=SearchResults)
async def get_history(
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get watch history."""
    ytmusic = YTMusicService(current_user)
    results = ytmusic.get_history()
    return {"results": results}

@router.post("/history/add", response_model=MessageResponse)
async def add_history_item(
    video_id: str = Body(..., embed=True),
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Add item to history."""
    ytmusic = YTMusicService(current_user)
    song = ytmusic.get_song(video_id=video_id)  # Get song details first
    result = ytmusic.add_history_item(song)
    return {"message": "History item added successfully"}

@router.post("/history/remove", response_model=MessageResponse)
async def remove_history_items(
    feedback_tokens: List[str] = Body(..., embed=True),
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Remove items from history."""
    ytmusic = YTMusicService(current_user)
    result = ytmusic.remove_history_items(feedback_tokens=feedback_tokens)
    return {"message": "History items removed successfully"}

@router.get("/uploads/songs", response_model=SearchResults)
async def get_library_upload_songs(
    limit: int = 25,
    order: Optional[LibraryOrderType] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get uploaded songs."""
    ytmusic = YTMusicService(current_user)
    results = ytmusic.get_library_upload_songs(limit=limit, order=order)
    return {"results": results}

@router.get("/uploads/artists", response_model=SearchResults)
async def get_library_upload_artists(
    limit: int = 25,
    order: Optional[LibraryOrderType] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get uploaded artists."""
    ytmusic = YTMusicService(current_user)
    results = ytmusic.get_library_upload_artists(limit=limit, order=order)
    return {"results": results}

@router.get("/uploads/albums", response_model=SearchResults)
async def get_library_upload_albums(
    limit: int = 25,
    order: Optional[LibraryOrderType] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get uploaded albums."""
    ytmusic = YTMusicService(current_user)
    results = ytmusic.get_library_upload_albums(limit=limit, order=order)
    return {"results": results}

@router.get("/uploads/artist/{browse_id}", response_model=SearchResults)
async def get_library_upload_artist(
    browse_id: str,
    limit: int = 25,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get uploaded artist details."""
    ytmusic = YTMusicService(current_user)
    results = ytmusic.get_library_upload_artist(browse_id=browse_id, limit=limit)
    return {"results": results}

@router.get("/uploads/album/{browse_id}")
async def get_library_upload_album(
    browse_id: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get uploaded album details."""
    ytmusic = YTMusicService(current_user)
    return ytmusic.get_library_upload_album(browse_id=browse_id)

@router.post("/uploads/song", response_model=MessageResponse)
async def upload_song(
    filepath: str = Body(..., embed=True),
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Upload a song."""
    ytmusic = YTMusicService(current_user)
    success = ytmusic.upload_song(filepath=filepath)
    return {"message": "Song uploaded successfully" if success else "Failed to upload song"}

@router.delete("/uploads/{entity_id}", response_model=MessageResponse)
async def delete_upload_entity(
    entity_id: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete an uploaded entity."""
    ytmusic = YTMusicService(current_user)
    success = ytmusic.delete_upload_entity(entity_id=entity_id)
    return {"message": "Entity deleted successfully" if success else "Failed to delete entity"} 
