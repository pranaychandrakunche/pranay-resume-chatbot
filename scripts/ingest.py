"""Rebuild the FAISS vector store from data/resume.md (or resume.pdf).

Usage (from repo root, venv active):
    python -m scripts.ingest
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO)

from app.rag.ingest import build_vectorstore  # noqa: E402


def main() -> None:
    store = build_vectorstore()
    print(f"Ingest complete. Vectors: {store.index.ntotal}")


if __name__ == "__main__":
    main()
