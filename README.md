# Pranay Chandra — Resume Chatbot

Recruiter-facing AI chatbot about **Kunche Pranay Chandra**.

**Stack:** FastAPI · LangChain · LangGraph · FAISS RAG · React (Vite) · Azure

## Quick start (local)

### 1. Backend

```powershell
cd c:\Users\prana\my_bot
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# ensure .env has OPENAI_API_KEY=...
python -m scripts.ingest
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```powershell
cd c:\Users\prana\my_bot\frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness + vectorstore status |
| POST | `/chat` | `{ "message": "...", "history": [] }`|

## Azure

See [azure/README.md](azure/README.md) for App Service (API) + Static Web Apps (React).

## Project layout

```
app/           FastAPI + LangGraph agent + RAG
data/          resume.md, resume.pdf, vectorstore/
frontend/      React chat UI
scripts/       ingest pipeline
azure/         Azure deploy notes
Dockerfile     API container
```
