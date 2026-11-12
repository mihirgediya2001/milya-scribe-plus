"""FastAPI application entry-point.

Run with:  ``uvicorn app.main:app --reload``  (from the ``backend/`` directory)
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import admin, auth, scribe

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Create DB tables on startup."""
    init_db()
    yield


app = FastAPI(title="Milya Scribe Plus", version="0.1.0", lifespan=lifespan)

# CORS (allow the frontend during development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(scribe.router)
app.include_router(admin.router)


# ---------------------------------------------------------------------------
# Frontend: serve static assets and HTML pages
# ---------------------------------------------------------------------------

if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")

    @app.get("/")
    @app.get("/login")
    def login_page():
        return FileResponse(FRONTEND_DIR / "login.html")

    @app.get("/signup")
    def signup_page():
        return FileResponse(FRONTEND_DIR / "signup.html")

    @app.get("/dashboard")
    def dashboard_page():
        return FileResponse(FRONTEND_DIR / "dashboard.html")

    @app.get("/scribe")
    def scribe_page():
        return FileResponse(FRONTEND_DIR / "scribe.html")


@app.get("/health")
def health():
    from app.config import settings

    return {
        "ok": True,
        "groq_configured": bool(settings.groq_api_key),
        "llm_model": settings.llm_model,
    }
