from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agents import router as agents_router
from app.api.analytics import router as analytics_router
from app.api.approvals import router as approvals_router
from app.api.audit_logs import router as audit_logs_router
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.monitoring import router as monitoring_router
from app.api.requests import router as requests_router
from app.api.tools import router as tools_router
from app.api.workflows import router as workflows_router
from app.api.background_jobs import router as background_jobs_router
from app.api.feedback import router as feedback_router

from app.core.database import close_database, init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables when application starts
    await init_database()

    yield

    # Close database connection when application stops
    await close_database()


app = FastAPI(
    title="AURIXA",
    description="Autonomous Enterprise AI Platform",
    version="0.1.0",
    lifespan=lifespan,
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://aurixa-k22m.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# API ROUTERS
# ==========================================

app.include_router(agents_router, prefix="/api/v1")
app.include_router(workflows_router, prefix="/api/v1")
app.include_router(approvals_router, prefix="/api/v1")
app.include_router(tools_router, prefix="/api/v1")
app.include_router(background_jobs_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")
app.include_router(audit_logs_router, prefix="/api/v1")
app.include_router(monitoring_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(requests_router, prefix="/api/v1")


# ==========================================
# ROOT
# ==========================================

@app.get("/")
async def root():
    return {
        "name": "AURIXA",
        "description": "Autonomous Enterprise AI Platform",
        "version": "0.1.0",
        "status": "running",
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }