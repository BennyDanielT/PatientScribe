from openai import OpenAI
from app.core.config.settings import settings
from app.core.config.logger import get_logger

logger = get_logger()

# Initialize the OpenAI client as None by default
client: OpenAI | None = None

if settings.OPENAI_API_KEY:
    try:
        # Create a single reusable OpenAI client
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("Centralized OpenAI client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
else:
    logger.warning(
        "No OPENAI_API_KEY provided. OpenAI client will not be initialized, falling back to mock behavior if dev mode allows."
    )
