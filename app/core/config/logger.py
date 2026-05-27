# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
# from app.core.config.native_logger import (
#     setup_logging,
#     get_logger,
# )  # ← Native (demo first)

from app.core.config.loguru_logger import (
    setup_logging,
    get_logger,
)
