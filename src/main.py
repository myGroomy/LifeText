"""FastAPI application entry point."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings
from src.db import init_db
from src.routers import transcribe, jobs, intelligence, chat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="LifeText API",
    description="AI-powered transcription SaaS",
    version="0.1.0"
)

settings = get_settings()

# CORS middleware - Secure configuration
# Development: Allow localhost only
# Production: Whitelist specific domains
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

# Add production domains if not in debug mode
if not settings.debug:
    allowed_origins = [
        "https://lifetext.app",
        "https://www.lifetext.app",
        "https://api.lifetext.app",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transcribe.router)
app.include_router(jobs.router)
app.include_router(intelligence.router)
app.include_router(chat.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "environment": settings.app_env}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "LifeText API",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
