"""
Authentication Routes

FastAPI route handlers for the auth module.
Provides REST API endpoints for authentication and user management.
"""

from fastapi import APIRouter
from .login import router as login_router
from .register import router as register_router
from .password import router as password_router

router = APIRouter(prefix="/auth", tags=["Authentication"])

router.include_router(login_router)
router.include_router(register_router)
router.include_router(password_router)

__all__ = ["router"]