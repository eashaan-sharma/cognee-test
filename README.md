# cognee-test

Middle-earth knowledge graph demo: Wikipedia articles → Cognee → knowledge graph → Q&A.
Sandbox for the KIST × Enterobiome "NGP Second Brain" project.

## Layout
- `backend/` – Python: fetch articles, build the graph, serve the API
- `frontend/` – React + Vite UI (carried over from the earlier knowledge-graph repo)
- `data/raw/` – downloaded articles (not committed)

## Setup
1. `uv sync` (or follow the setup steps)
2. Copy `.env.example` to `.env` and add your Gemini API key
3. Frontend: `cd frontend` then `npm install` and `npm run dev`
