"""
PatientScribe FastAPI Backend

Production-grade medical report simplification API with:
- Correlation ID-based distributed request tracing
- Loguru + RichHandler for beautiful, structured logging
- Automatic correlation ID injection in all logs via contextvars
"""

from fastapi import FastAPI, Request
from app.core.config.logger import setup_logging, get_logger
from app.middleware.correlation_middleware import (
    CorrelationIDMiddleware,
    get_correlation_id,
)
from app.api.routes import patient_routes, workflow_routes, record_routes

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

# Include routers
app.include_router(patient_routes.router, prefix="/patients")
app.include_router(workflow_routes.router)
app.include_router(record_routes.router)


# Example endpoint demonstrating automatic correlation logging
@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint demonstrating correlation logging."""
    logger.info("Health check requested")
    return {"status": "healthy", "service": "PatientScribe API"}


@app.get("/error")
async def error_endpoint(request: Request):
    """Example error endpoint demonstrating correlation logging with exceptions."""
    logger.info("Error endpoint hit")
    try:
        raise RuntimeError("Simulated endpoint error")
    except Exception as e:
        logger.error(f"Endpoint error: {e}")
        logger.critical("Critical issue encountered in endpoint!")
    return {"status": "error simulated"}
