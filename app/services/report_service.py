from app.core.config.logger import get_logger
from app.services.llm_service import simplify_with_llm

logger = get_logger()


async def simplify_report(report_text: str) -> dict:
    """
    Orchestrator service for medical report simplification.

    This layer coordinates processing:
    1. Future integrations: parsing, extracting entities, checking vector DB/cache.
    2. Calls the LLM Service to translate the raw report text.
    3. Future integrations: post-processing, validation, or compliance checks.

    Args:
        report_text (str): The raw text of the medical report.

    Returns:
        dict: A dictionary containing the simplified text and status.
    """
    logger.info("Report orchestrator service starting...")

    # NOTE: In future episodes, we can add:
    # - A parsing step to extract patient symptoms/vitals
    # - A vector DB query (RAG) to fetch relevant medical explanation guidelines

    # Delegate core translation/simplification to LLM service
    simplified_text = await simplify_with_llm(report_text)

    logger.info("Report orchestrator service finished successfully.")

    return {
        "status": "success",
        "simplified_text": simplified_text,
    }
