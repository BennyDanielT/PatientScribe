"""
LLM Service

This service handles interactions with Large Language Models for medical report simplification.
All logs automatically include the correlation ID via contextvars.
"""

from typing import Dict, Any, Optional
from app.core.config.logger import get_logger
from app.middleware.correlation_middleware import get_correlation_id

logger = get_logger()


async def simplify_report(
    medical_report: str, style: str = "patient_friendly", language: str = "english"
) -> Dict[str, Any]:
    """
    Use LLM to simplify medical report for patient understanding.

    Correlation ID is automatically included in all logs.
    Demonstrates using get_correlation_id() for external API calls.

    Args:
        medical_report (str): The medical report text to simplify
        style (str): Target simplification style ("patient_friendly", "clinical_summary", etc.)
        language (str): Target language for the simplified report

    Returns:
        Dict[str, Any]: Simplified report and metadata

    Example:
        >>> result = await simplify_report("Complex medical report...")
        >>> # Logs will automatically include: CID=<correlation-id>
    """
    logger.info(f"Starting report simplification (style={style}, language={language})")

    try:
        report_length = len(medical_report.split())
        logger.debug(f"Input report length: {report_length} words")

        # Get correlation ID for external API calls
        correlation_id = get_correlation_id()
        logger.debug(f"Using correlation ID for LLM API: {correlation_id}")

        logger.debug(f"Preparing LLM request with style={style}")

        logger.debug("Calling LLM API")
        # Simulate LLM call with correlation ID for distributed tracing
        simplified_text = f"[Simplified version of medical report in {language}]"

        logger.debug("Parsing LLM response")

        result = {
            "original_length": report_length,
            "simplified_text": simplified_text,
            "style": style,
            "language": language,
            "correlation_id": correlation_id,
            "status": "success",
        }

        logger.info("Report simplification completed successfully")

        return result

    except Exception as e:
        logger.error(f"Error simplifying report: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "correlation_id": get_correlation_id(),
        }


async def extract_key_points(medical_report: str) -> Dict[str, Any]:
    """
    Use LLM to extract key clinical points from medical report.

    Args:
        medical_report (str): The medical report to extract from

    Returns:
        Dict[str, Any]: Extracted key points and metadata
    """
    logger.info("Extracting key clinical points from report")

    try:
        logger.debug("Preparing LLM extraction prompt")

        logger.debug("Calling LLM for extraction")

        key_points = ["diagnosis", "treatment_plan", "follow_up_required"]

        logger.debug(f"Extracted {len(key_points)} key points")

        logger.info("Key point extraction completed")

        return {
            "key_points": key_points,
            "status": "success",
            "correlation_id": get_correlation_id(),
        }

    except Exception as e:
        logger.error(f"Error extracting key points: {e}")
        return {
            "status": "error",
            "error": str(e),
            "correlation_id": get_correlation_id(),
        }


async def generate_patient_summary(
    medical_report: str, include_instructions: bool = True
) -> str:
    """
    Generate a patient-friendly summary of medical report.

    Args:
        medical_report (str): The medical report to summarize
        include_instructions (bool): Whether to include follow-up instructions

    Returns:
        str: Patient-friendly summary text
    """
    logger.info(
        f"Generating patient summary (include_instructions={include_instructions})"
    )

    try:
        logger.debug("Analyzing report content")

        logger.debug("Generating patient-friendly language")

        if include_instructions:
            logger.debug("Adding follow-up instructions")

        summary = "[Patient-friendly medical summary]"

        logger.info("Patient summary generation completed")

        return summary

    except Exception as e:
        logger.error(f"Error generating patient summary: {e}")
        return f"Error: {str(e)}"
