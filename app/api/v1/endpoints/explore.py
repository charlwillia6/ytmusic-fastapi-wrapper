from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from app.core.security import get_current_user
from app.schemas.models import CredentialsModel, SearchResults
from app.services.ytmusic import YTMusicService

router = APIRouter()

@router.get("/moods", response_model=SearchResults)
async def get_mood_categories(
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get mood categories."""
    try:
        ytmusic = YTMusicService(current_user)
        results = ytmusic.get_mood_categories()
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/moods/{params}", response_model=SearchResults)
async def get_mood_playlists(
    params: str,
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get mood playlists."""
    try:
        ytmusic = YTMusicService(current_user)
        results = ytmusic.get_mood_playlists(params)
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/charts", response_model=SearchResults)
async def get_charts(
    country_code: str = "ZZ",
    current_user: CredentialsModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get charts for a country."""
    try:
        ytmusic = YTMusicService(current_user)
        results = ytmusic.get_charts(country_code)
        if isinstance(results, list):
            return {"results": results}
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 
