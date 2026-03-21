"""
Patient Routes

Routes for patient-related operations with automatic correlation ID logging.
All logs in this module automatically include the correlation ID.
"""

from fastapi import APIRouter, Request
from app.core.config.logger import get_logger
from app.middleware.correlation_middleware import get_correlation_id
from app.services import parser, embeddings, llm

router = APIRouter()
logger = get_logger()


@router.get("/health")
async def health(request: Request):
    """Health check endpoint with correlation logging."""
    logger.info("Health check endpoint called")
    return {"status": "ok", "service": "patient_routes"}


@router.post("/process-report")
async def process_medical_report(request: Request):
    """
    Process a medical report end-to-end.

    This endpoint demonstrates automatic correlation ID logging across:
    - Route handler
    - Document parser service
    - Embeddings service
    - LLM service

    All logs will include the same correlation ID automatically.
    """
    logger.info("Processing medical report request")

    try:
        # Simulate receiving a medical report
        report_text = "Patient presented with symptoms of hypertension..."
        logger.debug("Received medical report for processing")

        # Parse the document
        logger.info("Step 1: Parsing document")
        parse_result = await parser.parse_document("medical_report.pdf")
        logger.info(f"Parse result status: {parse_result.get('status')}")

        # Validate the document
        logger.info("Step 2: Validating document")
        is_valid = await parser.validate_document("medical_report.pdf")
        logger.info(f"Document valid: {is_valid}")

        # Generate embeddings for semantic search
        logger.info("Step 3: Generating embeddings")
        text_chunks = await embeddings.chunk_text_for_embeddings(report_text)
        logger.debug(f"Created {len(text_chunks)} text chunks")

        embeddings_result = await embeddings.generate_embeddings(report_text)
        logger.info(f"Generated embeddings with dimension: {len(embeddings_result)}")

        # Simplify the report using LLM
        logger.info("Step 4: Simplifying report with LLM")
        simplified = await llm.simplify_report(report_text, style="patient_friendly")
        logger.info(f"Report simplification status: {simplified.get('status')}")

        # Extract key points
        logger.info("Step 5: Extracting key clinical points")
        key_points = await llm.extract_key_points(report_text)
        logger.info(f"Extracted {len(key_points.get('key_points', []))} key points")

        # Generate patient summary
        logger.info("Step 6: Generating patient summary")
        summary = await llm.generate_patient_summary(report_text)
        logger.info("Patient summary generated successfully")

        logger.info("Medical report processing completed successfully")

        # Return correlation ID for client reference
        return {
            "status": "success",
            "correlation_id": get_correlation_id(),
            "parse_status": parse_result.get("status"),
            "document_valid": is_valid,
            "embeddings_dimension": len(embeddings_result),
            "simplified_status": simplified.get("status"),
            "key_points_count": len(key_points.get("key_points", [])),
        }

    except Exception as e:
        logger.error(f"Error processing medical report: {e}", exc_info=True)
        return {
            "status": "error",
            "correlation_id": get_correlation_id(),
            "error": str(e),
        }


@router.get("/reports/{report_id}")
async def get_report(report_id: int, request: Request):
    """
    Retrieve a specific patient report.

    Demonstrates correlation logging in database queries.
    """
    logger.info(f"Fetching report ID: {report_id}")

    try:
        if report_id < 0:
            logger.warning(f"Invalid report ID provided: {report_id}")
            return {
                "error": "Invalid report ID",
                "correlation_id": get_correlation_id(),
            }

        logger.debug(f"Querying database for report {report_id}")

        # Simulate database query
        report_data = {
            "report_id": report_id,
            "patient_name": f"Patient {report_id}",
            "diagnosis": "Sample diagnosis",
            "date": "2024-03-07",
        }

        logger.info(f"Successfully retrieved report {report_id}")

        return {"report": report_data, "correlation_id": get_correlation_id()}

    except Exception as e:
        logger.error(f"Error retrieving report: {e}")
        return {"error": str(e), "correlation_id": get_correlation_id()}
