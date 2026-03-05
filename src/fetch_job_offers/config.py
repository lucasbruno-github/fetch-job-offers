"""Central configuration loaded from .env at project root."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project root is three levels up from this file (src/fetch_job_offers/config.py)
BASE_DIR = Path(__file__).parent.parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings:
    # --- LLM ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    # --- Email ---
    GMAIL_USER: str = os.getenv("GMAIL_USER", "")
    GMAIL_APP_PASSWORD: str = os.getenv("GMAIL_APP_PASSWORD", "")
    RECIPIENT_EMAIL: str = os.getenv("RECIPIENT_EMAIL", "")

    # --- User files (placed in project root) ---
    CV_PATH: Path = BASE_DIR / "cv.md"
    TEMPLATE_PATH: Path = BASE_DIR / "cover_letter_template.md"
    SEEN_JOBS_PATH: Path = BASE_DIR / "seen_jobs.json"

    # --- Search parameters ---
    SEARCH_QUERY: str = os.getenv("SEARCH_QUERY", "Data Scientist")
    LINKEDIN_LOCATION: str = os.getenv("LINKEDIN_LOCATION", "")
    HOURS_OLD: int = int(os.getenv("HOURS_OLD", "24"))
    MAX_JOBS: int = int(os.getenv("MAX_JOBS", "5"))

    def validate(self) -> None:
        """Raise ValueError for any missing required settings."""
        missing = []
        for field in ("GEMINI_API_KEY", "GMAIL_USER", "GMAIL_APP_PASSWORD", "RECIPIENT_EMAIL"):
            if not getattr(self, field):
                missing.append(field)
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please fill in your .env file (see CLAUDE.md for the template)."
            )
        if not self.CV_PATH.exists():
            raise FileNotFoundError(f"CV file not found: {self.CV_PATH}")
        if not self.TEMPLATE_PATH.exists():
            raise FileNotFoundError(f"Cover letter template not found: {self.TEMPLATE_PATH}")


settings = Settings()
