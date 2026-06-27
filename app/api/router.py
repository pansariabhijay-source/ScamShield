from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import admin, auth, detect, history, stats

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(detect.router)
api_router.include_router(history.router)
api_router.include_router(admin.router)
api_router.include_router(stats.router)
