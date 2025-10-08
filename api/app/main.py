"""
FastAPI main application entry point.
Customer AI Driven Feedback Analyzer API.
"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time

from app.config import settings
from app.routes import upload, status, results, export, health, metrics
from app.utils.logging import setup_logging


# Setup structured logging
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Customer Feedback Analyzer API", version="3.1.0")
    yield
    logger.info("Shutting down API")


app = FastAPI(
    title="Customer AI Driven Feedback Analyzer",
    description="Analyze customer feedback using AI to extract emotions, NPS, and insights",
    version="3.1.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
    redirect_slashes=False  # IMPORTANT: Disable automatic trailing slash redirects
)

# Security middleware
if not settings.is_development:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.onrender.com", "localhost", "customer-feedback-api-bmjp"]
    )

# Note: CORS is not needed since API is private and accessed only via BFF proxy


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()

    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client=request.client.host if request.client else None
    )

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )

    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        method=request.method,
        url=str(request.url),
        exc_info=True
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": str(exc) if settings.is_development else "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(status.router, prefix="/status", tags=["status"])
app.include_router(results.router, prefix="/results", tags=["results"])
app.include_router(export.router, prefix="/export", tags=["export"])
app.include_router(metrics.router)  # Metrics router (already has /api/metrics prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Customer AI Driven Feedback Analyzer",
        "version": "3.1.0",
        "status": "healthy",
        "docs": "/docs" if settings.is_development else None
    }