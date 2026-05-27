# Episode 3 Walkthrough: First Real LLM Endpoint

This document outlines the production-grade implementation of the first real LLM endpoint for **PatientScribe**, replacing placeholder report simplification logic with a real OpenAI-powered workflow.

---

## 📂 Phase 1: Folder Structure

The project has been organized into a modular, clean, and scalable architecture. Below is the updated directory structure:

```text
PatientScribe/
├── .env                          # Local environment secrets
├── requirements-prod.txt         # Production dependencies (fastapi, openai, etc.)
├── requirements-dev.txt          # Local development dependencies (mypy, black, etc.)
└── app/
    ├── main.py                   # FastAPI application entry point
    ├── api/
    │   └── routes/
    │       ├── health_routes.py  # Service health check endpoint
    │       └── patient_routes.py # POST /patients/simplify-report
    ├── core/
    │   └── config/
    │       ├── logger.py         # Logger setup toggle (native vs loguru)
    │       ├── loguru_logger.py  # Production Loguru configuration with correlation IDs
    │       ├── openai_client.py  # Centralized & reusable OpenAI client instance
    │       └── settings.py       # Pydantic-validated environment configuration
    ├── middleware/
    │   └── correlation_middleware.py # Request tracing middleware using contextvars
    ├── prompts/
    │   └── simplify_report.txt   # Externalized prompt template
    ├── schemas/
    │   └── patient.py            # Pydantic request & response validators
    └── services/
        ├── llm_service.py        # Logic for reading prompts and calling OpenAI in a thread pool
        └── report_service.py     # Service orchestrator layer for medical reports
```

---

## 💻 Phase 2: Full Code for Each File

Here is the complete source code for each of the core files involved in **Episode 3**.

### 1. Settings Configuration
**File:** [settings.py](file:///c:/Users/benny/OneDrive/Desktop/Projects/PatientScribe/app/core/config/settings.py)
*Loads secrets and configurations from `.env` using python-dotenv, validates them using Pydantic, and handles mock behavior flag.*

```python
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
```

---

### 2. OpenAI Centralized Client
**File:** [openai_client.py](file:///c:/Users/benny/OneDrive/Desktop/Projects/PatientScribe/app/core/config/openai_client.py)
*Prevents initialization of the OpenAI client on every request, avoiding socket/resource exhaustion.*

```python
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
```

---

### 3. Pydantic Schemas
**File:** [patient.py](file:///c:/Users/benny/OneDrive/Desktop/Projects/PatientScribe/app/schemas/patient.py)
*Provides validation, clear descriptive error responses, and Swagger documentation metadata.*

```python
from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """
    Request payload containing the patient ID and the raw medical report text.
    """

    patient_id: str = Field(
        ..., description="The unique identifier for the patient.", examples=["P001"]
    )
    report_text: str = Field(
        ...,
        description="The raw medical report text containing jargon to simplify.",
        examples=["MRI shows mild disc bulge at L4-L5."],
    )


class ReportResponse(BaseModel):
    """
    Response payload containing the simplified medical report and execution status.
    """

    status: str = Field(
        ...,
        description="The status of the simplification operation (e.g., 'success' or 'mock_success').",
        examples=["success"],
    )
    patient_id: str = Field(
        ..., description="The unique identifier for the patient.", examples=["P001"]
    )
    simplified_text: str = Field(
        ...,
        description="The simplified explanation of the medical report in plain English.",
        examples=["There is a small bulging disc in the lower back..."],
    )
```

---

### 4. External Prompt Template
**File:** [simplify_report.txt](file:///c:/Users/benny/OneDrive/Desktop/Projects/PatientScribe/app/prompts/simplify_report.txt)
*Keeps instructions for the LLM separated from Python logic, facilitating prompt updates and version control.*

```text
You are PatientScribe, an empathetic, senior medical communicator. Your goal is to translate complex, jargon-heavy medical reports into simple, friendly, and easy-to-understand English for patients.

Follow these strict rules:
1. Translating Medical Jargon: Explain medical terms in plain English. For example, instead of "mild disc bulge at L4-L5", explain that there is a slight bulge in one of the cushions (discs) in the lower back.
2. No Diagnosis or Treatment Claims: Do not diagnose the patient or suggest treatments. Explicitly maintain a supportive but informational role. Never say "You have X disease" or "You need Y surgery." Focus purely on explaining the findings of the report.
3. Structure & Format: Make the response concise, clear, and user-friendly. Use a brief, reassuring intro (1-2 sentences), followed by simple bullet points for key findings if appropriate, and end with a reminder to consult their healthcare provider.
4. Tone: Reassuring, clear, and professional.

Input medical report text:
{report_text}
```

---

### 5. LLM Integration Service
**File:** [llm_service.py](file:///c:/Users/benny/OneDrive/Desktop/Projects/PatientScribe/app/services/llm_service.py)
*Reads the prompt template, coordinates API calling in a separate thread pool (`asyncio.to_thread`) to prevent blocking the async event loop, and includes a mock fallback in development mode if no API key is specified.*

```python
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
```

---

### 6. Report Service Orchestrator
**File:** [report_service.py](file:///c:/Users/benny/OneDrive/Desktop/Projects/PatientScribe/app/services/report_service.py)
*The business entry-point. Acts as an orchestration layer, making it easy to add parsing, vector databases, or audit layers in future episodes.*

```python
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
```

---

### 7. Patient API Router
**File:** [patient_routes.py](file:///c:/Users/benny/OneDrive/Desktop/Projects/PatientScribe/app/api/routes/patient_routes.py)
*Binds the FastAPI framework. Ensures request/response validation, handles errors, and produces trace logs.*

```python
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
```

---

## ⚙️ Phase 3: How to Run Locally

### 1. Set Up Environment Variables
Create a file named `.env` in the root directory (where `requirements.txt` is located):

```env
# OpenAI Configurations
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Application Settings
APP_ENV=dev
```

### 2. Install Dependencies
Activate your virtual environment and install the required modules:

```bash
# Windows
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Run the Backend Server
Start the Uvicorn server in reload mode:

```bash
python -m uvicorn app.main:app --reload
```

Uvicorn will spin up locally, listening on `http://127.0.0.1:8000`.

---

## 🧪 Phase 4: Sample Request

### Option A: Testing via curl (Command Line)
You can invoke the endpoint via your command line (making sure to pass an `X-Correlation-ID` header if you want to trace it specifically, though the middleware will auto-generate one if omitted):

```bash
curl -X POST "http://127.0.0.1:8000/patients/simplify-report" \
     -H "Content-Type: application/json" \
     -H "X-Correlation-ID: yt-demo-12345" \
     -d "{\"patient_id\": \"P001\", \"report_text\": \"MRI shows mild disc bulge at L4-L5.\"}"
```

**Expected JSON Response:**
```json
{
  "status": "success",
  "patient_id": "P001",
  "simplified_text": "**Here is a simplified summary of your report:**\n\n• **Bulging Disc:** There is a slight bulging of one of the cushions (discs) in your lower back (between the L4 and L5 bones).\n• **No Diagnosis:** This is a common finding and does not automatically point to a severe medical condition or treatment.\n\n*(Please discuss these findings with your doctor to understand what they mean for your health.)*"
}
```

### Option B: Testing via Interactive Swagger UI
1. Open your browser and navigate to `http://127.0.0.1:8000/docs`.
2. Expand the `POST /patients/simplify-report` endpoint.
3. Click **Try it out**, edit the payload, and click **Execute**.
4. Examine the detailed Request Headers, Response Body, and Response Headers (where you will see the returned `X-Correlation-ID` header).

---

## 🎥 Phase 5: YouTube Episode Demo Points

During **Episode 3**, you can showcase these high-value engineering design decisions:

1. **Separation of Concerns**: Show the viewer that the controller (routes) validates the JSON shape, the service orchestrator (`report_service.py`) decides what business steps to take, and the `llm_service.py` is dedicated to prompt loading and API communications.
2. **Avoiding Event-Loop Blocking (`asyncio.to_thread`)**: Explain that calling `client.chat.completions.create` is a synchronous network request. In FastAPI, if you make synchronous network calls directly within `async def` functions, you block the single-threaded event loop! Using `asyncio.to_thread()` offloads this call to a background thread pool, keeping the API responsive for concurrent requests (e.g. other health checks).
3. **Graceful Fallback / Mock Mode**: Show that when you rename `.env` to disable the API Key, the application doesn't crash. It outputs a helpful warning log and provides a clean mock translation with a built-in `await asyncio.sleep(0.8)` to simulate API response latency. This is perfect for viewers who want to play with the code without having an active paid OpenAI key.
4. **Loguru Log Interception and Correlation ID**:
   - Send a request using Swagger or `curl`.
   - Show how the correlation ID (`yt-demo-12345`) is automatically printed on every single log line in the console through the contextvars patcher—even inside the background thread spawned by `asyncio.to_thread`.
   - Point out that this is critical for tracing individual requests in production environments.
