"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "pranay-resume-chatbot"
    app_env: str = "local"
    debug: bool = True

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # Profile
    candidate_name: str = "Pranay"
    candidate_full_name: str = "Kunche Pranay Chandra"

    # RAG paths
    resume_md_path: str = str(ROOT_DIR / "data" / "resume.md")
    resume_pdf_path: str = str(ROOT_DIR / "data" / "resume.pdf")
    vectorstore_path: str = str(ROOT_DIR / "data" / "vectorstore")

    # Retrieval
    retrieval_k: int = 4
    chunk_size: int = 800
    chunk_overlap: int = 120

    # CORS — comma-separated origins; "*" allowed for local
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
