"""
CareerCraft AI — FastAPI Application Entry Point
"""

import os
import sys

# Ensure `backend/` is on the path so `routers` and `core` are importable
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(_backend_dir), ".env"))
load_dotenv(os.path.join(_backend_dir, ".env"), override=True)
load_dotenv()

from routers import analyze, match, builder, interview, export

app = FastAPI(
    title="CareerCraft AI",
    description="Groq-powered Resume Analyzer, Job Matcher & Resume Builder",
    version="1.0.0",
)

# ── CORS — allow frontend (served from same origin or different port) ─────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ────────────────────────────────
app.include_router(analyze.router,   prefix="/api", tags=["Analyze"])
app.include_router(match.router,     prefix="/api", tags=["Match"])
app.include_router(builder.router,   prefix="/api", tags=["Builder"])
app.include_router(interview.router, prefix="/api", tags=["Interview"])
app.include_router(export.router,    prefix="/api", tags=["Export"])


# ── Serve Frontend Static Files ───────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.isdir(FRONTEND_DIR):
    css_dir = os.path.join(FRONTEND_DIR, "css")
    js_dir = os.path.join(FRONTEND_DIR, "js")

    if os.path.isdir(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    if os.path.isdir(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")

    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{page}.html")
    async def serve_page(page: str):
        filepath = os.path.join(FRONTEND_DIR, f"{page}.html")
        if os.path.exists(filepath):
            return FileResponse(filepath)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{page}")
    async def serve_clean_page(page: str):
        filepath = os.path.join(FRONTEND_DIR, f"{page}.html")
        if os.path.exists(filepath):
            return FileResponse(filepath)
        raw_filepath = os.path.join(FRONTEND_DIR, page)
        if os.path.exists(raw_filepath) and os.path.isfile(raw_filepath):
            return FileResponse(raw_filepath)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))



@app.get("/api/health")
async def health():
    return {"status": "ok", "model": "openai/gpt-oss-120b"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
