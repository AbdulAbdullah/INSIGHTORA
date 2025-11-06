"""
Main API Router

Aggregates all API endpoints with proper versioning.
"""

from fastapi import APIRouter

from app.modules.auth.routes import router as auth_router

api_router = APIRouter()

api_router.include_router(auth_router, tags=["Authentication"])

@api_router.get("/health")
async def health_check():
    """API health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}