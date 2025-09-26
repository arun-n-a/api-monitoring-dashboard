from fastapi import APIRouter

from app.api.endpoints import (
    auth, 
    users,
    prompts,
    documents,
    open_ai,
    display_logs
    )

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)
