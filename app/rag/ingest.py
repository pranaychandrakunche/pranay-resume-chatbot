"""Build / rebuild the FAISS vector store from resume sources."""

from __future__ import annotations

import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


def _load_documents(settings: Settings):
    docs = []
    md_path = Path(settings.resume_md_path)
    pdf_path = Path(settings.resume_pdf_path)

    if md_path.exists():
        loaded = TextLoader(str(md_path), encoding="utf-8").load()
        for d in loaded:
            d.metadata["source"] = "resume.md"
        docs.extend(loaded)
        logger.info("Loaded markdown resume: %s", md_path)
    elif pdf_path.exists():
        loaded = PyPDFLoader(str(pdf_path)).load()
        for d in loaded:
            d.metadata["source"] = "resume.pdf"
        docs.extend(loaded)
        logger.info("Loaded PDF resume: %s", pdf_path)
    else:
        raise FileNotFoundError(
            f"No resume found at {md_path} or {pdf_path}. Place resume.md or resume.pdf in data/."
        )

    return docs


def build_vectorstore(settings: Settings | None = None) -> FAISS:
    settings = settings or get_settings()
    docs = _load_documents(settings)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    logger.info("Split resume into %d chunks", len(chunks))

    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key,
    )
    store = FAISS.from_documents(chunks, embeddings)

    out = Path(settings.vectorstore_path)
    out.mkdir(parents=True, exist_ok=True)
    store.save_local(str(out))
    logger.info("Saved FAISS index to %s", out)
    return store


def load_vectorstore(settings: Settings | None = None) -> FAISS:
    settings = settings or get_settings()
    path = Path(settings.vectorstore_path)
    index_file = path / "index.faiss"

    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key,
    )

    if index_file.exists():
        return FAISS.load_local(
            str(path),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    logger.warning("Vector store missing — building now")
    return build_vectorstore(settings)
