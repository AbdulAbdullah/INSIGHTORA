"""
Main API router that includes all route modules
"""

from fastapi import APIRouter
from app.api import auth, data_sources, queries, dashboards

api_router = APIRouter()

# Include all route modules with prefixes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    data_sources.router,
    prefix="/data-sources",
    tags=["Data Sources"]
)

api_router.include_router(
    queries.router,
    prefix="/queries",
    tags=["Queries"]
)

api_router.include_router(
    dashboards.router,
    prefix="/dashboards",
    tags=["Dashboards"]
)

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """
    Simple health check endpoint
    """
    return {"status": "healthy", "message": "Smart BI Platform API is running"}