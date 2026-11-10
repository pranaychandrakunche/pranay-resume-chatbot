"""FastAPI entrypoint for Pranay's resume chatbot."""

import logging
from contextlib import asynccontextmanager


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, health
from app.config import get_settings
import os
from azure.monitor.opentelemetry import configure_azure_monitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Warm the vector store / graph on startup so the first chat is fast."""
    settings = get_settings()
    try:
        from app.agent.graph import get_graph
        from app.rag.ingest import load_vectorstore

        load_vectorstore(settings)
        get_graph()
        logger.info("RAG vector store and LangGraph ready")
    except Exception:
        logger.exception(
            "Startup warm-up failed — /chat may rebuild the index on first request"
        )
    yield


def create_app() -> FastAPI:
    if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        configure_azure_monitor()

    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Recruiter-facing resume chatbot for Kunche Pranay Chandra.",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router)

    @app.get("/")
    def root():
        return {
            "message": f"Hi — I'm {settings.candidate_name}'s resume API.",
            "health": "/health",
            "chat": "POST /chat",
        }

    return app


app = create_app()
