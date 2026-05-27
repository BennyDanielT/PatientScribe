import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from app.core.config.logger import get_logger

logger = get_logger()

# Resolve path to the root directory where the .env file is located
ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = ROOT_DIR / ".env"

# Load the environment variables from the .env file
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    logger.info(f"Loaded environment variables from: {ENV_PATH}")
else:
    logger.warning(
        f"No .env file found at {ENV_PATH}, using system environment variables."
    )


class Settings(BaseModel):
    """
    Application settings validated via Pydantic.
    Allows easy access to environment configuration with clean typing.
    """

    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    APP_ENV: str = Field(default="dev")

    @property
    def is_dev(self) -> bool:
        return self.APP_ENV.lower() in ("dev", "development")


# Expose a single, centralized settings object
settings = Settings(
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
    OPENAI_MODEL=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    APP_ENV=os.getenv("APP_ENV", "dev"),
)

# Warn if OpenAI API Key is missing and we are in development mode
if not settings.OPENAI_API_KEY:
    if settings.is_dev:
        logger.warning(
            "OPENAI_API_KEY is not set. The application will run in MOCK mode for LLM operations."
        )
    else:
        logger.error(
            "OPENAI_API_KEY is not set in non-development environment! LLM calls will fail."
        )
