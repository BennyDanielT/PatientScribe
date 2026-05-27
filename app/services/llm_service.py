import asyncio
from pathlib import Path
from app.core.config.logger import get_logger
from app.core.config.openai_client import client
from app.core.config.settings import settings

logger = get_logger()

# Path to the external prompt template
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "simplify_report.txt"


def _read_prompt_template() -> str:
    """Reads the prompt template from the filesystem."""
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read prompt file at {PROMPT_PATH}: {e}")
        raise RuntimeError(f"Prompt template could not be loaded: {e}")


def _call_openai_sync(prompt: str) -> str:
    """
    Synchronous helper to interact with OpenAI API.
    Executed in a thread pool to avoid blocking the async event loop.
    """
    if not client:
        raise RuntimeError("OpenAI client is not initialized.")

    logger.debug(f"Sending request to OpenAI using model: {settings.OPENAI_MODEL}")

    # Call OpenAI API
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    # Extract the response text
    content = response.choices[0].message.content
    if not content:
        raise ValueError("OpenAI returned an empty response.")

    return content.strip()


async def simplify_with_llm(report_text: str) -> str:
    """
    Simplifies medical reports using OpenAI's API.

    If in development environment and the OpenAI key is missing,
    it falls back to a mock translation to ensure the application still runs.

    Args:
        report_text (str): The raw medical report text.

    Returns:
        str: The simplified explanation in plain English.
    """
    logger.info("LLM service started report simplification.")

    # 1. Graceful Mock Fallback for Local Dev
    if not settings.OPENAI_API_KEY:
        if settings.is_dev:
            logger.warning(
                "OPENAI_API_KEY is missing. Falling back to Mock translation (Dev Mode)."
            )
            # Mimic some small network/processing latency
            await asyncio.sleep(0.8)

            # Simple mock response demonstrating the format
            mock_response = (
                "**Here is a simplified summary of your report:**\n\n"
                "• **Bulging Disc:** There is a slight bulging of one of the cushions (discs) "
                "in your lower back (between the L4 and L5 bones).\n"
                "• **No Diagnosis:** This is a common finding and does not automatically "
                "point to a severe medical condition or treatment.\n\n"
                "*(Please discuss these findings with your doctor to understand what they mean for your health.)*"
            )
            logger.info("LLM service successfully completed (MOCK response).")
            return mock_response
        else:
            logger.error(
                "LLM service failed: OPENAI_API_KEY is missing in non-dev environment."
            )
            raise ValueError("OPENAI_API_KEY is required in production.")

    # 2. Production Path with Real LLM Call
    try:
        # Load and format the prompt
        logger.debug("Loading prompt template...")
        prompt_template = _read_prompt_template()
        prompt = prompt_template.format(report_text=report_text)

        logger.info("Calling OpenAI API (running in thread pool)...")
        # Run synchronous OpenAI call in a separate thread to prevent blocking
        # ContextVars (like correlation ID) are automatically propagated in python 3.11+
        simplified_text = await asyncio.to_thread(_call_openai_sync, prompt)

        logger.info("LLM service successfully completed OpenAI API call.")
        return simplified_text

    except Exception as e:
        logger.error(
            f"LLM service encountered an error during simplification: {e}",
            exc_info=True,
        )
        raise
