from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    browse,
    explore,
    library,
    playlists,
    podcasts,
    search,
    uploads,
    watch
)

router = APIRouter()

# Include all routers
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(browse.router, prefix="/browse", tags=["browse"])
router.include_router(explore.router, prefix="/explore", tags=["explore"])
router.include_router(library.router, prefix="/library", tags=["library"])
router.include_router(playlists.router, prefix="/playlists", tags=["playlists"])
router.include_router(podcasts.router, prefix="/podcasts", tags=["podcasts"])
router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
router.include_router(watch.router, prefix="/watch", tags=["watch"]) 
