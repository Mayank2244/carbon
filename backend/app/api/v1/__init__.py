"""API v1 routes initialization."""

from fastapi import APIRouter
from app.api.v1 import query, files, auth

router = APIRouter(prefix="/api/v1")
router.include_router(query.router)
router.include_router(files.router)
router.include_router(auth.router)

__all__ = ["router"]
