from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any, List, Optional
from app.core.security import get_current_user
from app.schemas.models import (
    CredentialsModel,
    SearchResults,
    MessageResponse,
    UploadArtistResponse,
    UploadAlbumResponse
)
from app.services.ytmusic import YTMusicService, LibraryOrderType

router = APIRouter()

@router.post("/songs", response_model=MessageResponse)
async def upload_song(
    filepath: str = Body(..., embed=True),
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Upload a song."""
    try:
        ytmusic = YTMusicService(current_user)
        success = ytmusic.upload_song(filepath=filepath)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to upload song"
            )
        return {"message": "Song uploaded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/entities/{entity_id}", response_model=MessageResponse)
async def delete_upload_entity(
    entity_id: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete an uploaded entity (song or album)."""
    try:
        ytmusic = YTMusicService(current_user)
        success = ytmusic.delete_upload_entity(entity_id=entity_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found or could not be deleted"
            )
        return {"message": "Upload entity deleted successfully"}
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/songs", response_model=SearchResults)
async def get_library_upload_songs(
    limit: int = 25,
    order: Optional[LibraryOrderType] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get uploaded songs."""
    try:
        ytmusic = YTMusicService(current_user)
        results = ytmusic.get_library_upload_songs(limit=limit, order=order)
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/artists", response_model=SearchResults)
async def get_library_upload_artists(
    limit: int = 25,
    order: Optional[LibraryOrderType] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get uploaded artists."""
    try:
        ytmusic = YTMusicService(current_user)
        results = ytmusic.get_library_upload_artists(limit=limit, order=order)
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/albums", response_model=SearchResults)
async def get_library_upload_albums(
    limit: int = 25,
    order: Optional[LibraryOrderType] = None,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get uploaded albums."""
    try:
        ytmusic = YTMusicService(current_user)
        results = ytmusic.get_library_upload_albums(limit=limit, order=order)
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/artists/{browse_id}", response_model=SearchResults)
async def get_library_upload_artist(
    browse_id: str,
    limit: int = 25,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get uploaded artist details."""
    try:
        ytmusic = YTMusicService(current_user)
        results = ytmusic.get_library_upload_artist(browse_id=browse_id, limit=limit)
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artist {browse_id} not found"
            )
        return {"results": results}
    except Exception as e:
        if "not found" in str(e).lower() or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/albums/{browse_id}", response_model=UploadAlbumResponse)
async def get_library_upload_album(
    browse_id: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get uploaded album details."""
    try:
        ytmusic = YTMusicService(current_user)
        album = ytmusic.get_library_upload_album(browse_id=browse_id)
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Album {browse_id} not found"
            )
        return {"album": album}
    except Exception as e:
        if "not found" in str(e).lower() or not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 
