# Backend API image for Azure App Service / Container Apps
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY data ./data
COPY scripts ./scripts

# Build vector index at image build time if OPENAI_API_KEY is passed as build-arg.
# Prefer runtime ingest in Azure if you rotate keys; startup will rebuild if missing.
ARG OPENAI_API_KEY=""
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
RUN if [ -n "$OPENAI_API_KEY" ]; then python -m scripts.ingest; fi

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
