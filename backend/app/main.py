"""
TaskFlow API - Main application entry point.

This module initializes the FastAPI application with:
- CORS middleware for frontend communication
- Session middleware for Google OAuth
- Background scheduler for deadline reminders
- API router registration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

from app.core.config import settings
from app.core.database import engine, Base
from app.models import *
from app.api.v1 import router as v1_router
from app.scheduler.tasks import send_deadline_reminders
from apscheduler.schedulers.background import BackgroundScheduler


# ========== Application Initialization ==========

app = FastAPI(
    title="TaskFlow API",
    description="Task and project management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ========== Middleware Configuration ==========

# CORS Configuration - Allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Session middleware for Google OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="taskflow_session"
)


# ========== Router Registration ==========

app.include_router(v1_router, prefix="/api/v1")


# ========== Root Endpoints ==========

@app.get("/")
async def root():
    return {
        "message": "TaskFlow API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}


# ========== Background Scheduler ==========

scheduler = BackgroundScheduler()
scheduler.add_job(
    send_deadline_reminders,
    'interval',
    hours=12,
    id='deadline_reminders',
    replace_existing=True
)
scheduler.start()


# ========== Shutdown Handler ==========

@app.on_event("shutdown")
def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()


# ========== Development Server ==========

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )