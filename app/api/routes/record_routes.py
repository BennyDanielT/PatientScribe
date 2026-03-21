"""Record Routes

Routes for record management with automatic correlation ID logging.
"""

from fastapi import APIRouter, Request
from app.core.config.logger import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/records/{record_id}")
async def get_record(record_id: int, request: Request):
    """Retrieve a specific record by ID."""
    logger.info(f"Fetching record {record_id}")
    if record_id < 0:
        logger.error("Invalid record ID")
        return {"error": "Invalid record ID"}
    logger.debug(f"Record {record_id} fetched")
    return {"record_id": record_id, "data": f"record{record_id}"}
