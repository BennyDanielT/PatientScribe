from fastapi import APIRouter
from app.core.config.logger import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/health")
async def health_check():
    logger.info("Health check requested")
    return {"status": "healthy", "service": "PatientScribe API"}
