from fastapi import APIRouter, HTTPException, status
from app.core.config.logger import get_logger
from app.schemas.patient import ReportRequest, ReportResponse
from app.services.report_service import simplify_report

router = APIRouter()
logger = get_logger()


@router.post(
    "/simplify-report",
    response_model=ReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Simplify a medical report",
    description="Accepts a raw medical report with complex jargon and returns a simplified version for the patient.",
)
async def simplify_patient_report(payload: ReportRequest) -> ReportResponse:
    """
    Endpoint to receive medical report text, validate the payload,
    call the services orchestrator, and return the simplified text.
    """
    logger.info(
        f"API Route: Received simplification request for patient: {payload.patient_id}"
    )

    try:
        # Orchestrate the report simplification
        result = await simplify_report(payload.report_text)

        logger.info(
            f"API Route: Successfully simplified report for patient: {payload.patient_id}"
        )

        # Build and return the response object matching the ReportResponse schema
        return ReportResponse(
            status=result.get("status", "success"),
            patient_id=payload.patient_id,
            simplified_text=result.get("simplified_text", ""),
        )

    except Exception as e:
        logger.error(
            f"API Route: Failed to simplify report for patient {payload.patient_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while simplifying the report: {str(e)}",
        )
