"""Chat endpoint backed by LangGraph RAG agent."""

import logging

from fastapi import APIRouter, HTTPException

from app.agent.graph import run_chat
from app.schemas.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        history = [m.model_dump() for m in request.history]
        reply, sources = run_chat(request.message, history)
        return ChatResponse(reply=reply, sources=sources)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:
        logger.exception("Chat failed")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong generating a reply. Please try again.",
        ) from None
