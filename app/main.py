"""
PatientScribe FastAPI Backend

Production-grade medical report simplification API with:
- Correlation ID-based distributed request tracing
- Loguru + RichHandler for beautiful, structured logging
- Automatic correlation ID injection in all logs via contextvars
"""

from fastapi import FastAPI, Request
from app.core.config.logger import setup_logging, get_logger
from app.middleware.correlation_middleware import CorrelationIDMiddleware
from app.api.routes import patient_routes, health_routes

# Initialize logger
logger = setup_logging()

# Create FastAPI application
app = FastAPI(
    title="PatientScribe API",
    description="Backend for medical report simplification with correlation logging",
    version="1.0.0",
)

# Register middleware in order (middleware processes requests bottom-to-top)
# Correlation ID middleware must be early to track the entire request
app.add_middleware(CorrelationIDMiddleware)

app.include_router(health_routes.router, tags=["health"])
app.include_router(patient_routes.router, prefix="/patients", tags=["patients"])
