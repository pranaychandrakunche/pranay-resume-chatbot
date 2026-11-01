"""Health check."""

from pathlib import Path

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    vs = Path(settings.vectorstore_path) / "index.faiss"
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "candidate": settings.candidate_full_name,
        "vectorstore_ready": vs.exists(),
    }
