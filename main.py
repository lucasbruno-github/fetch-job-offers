"""
Entry point — run manually to trigger the full job digest pipeline.

Usage:
    uv run python main.py
    # or with the venv activated:
    python main.py

Prerequisites (see CLAUDE.md):
    - cv.md               : your CV in Markdown format
    - cover_letter_template.md : your cover letter template
    - .env                : GEMINI_API_KEY, GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL
"""

import logging
import sys

# Configure logging before importing project modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)

from fetch_job_offers.agents.orchestrator import OrchestratorAgent
from fetch_job_offers.config import settings


def main() -> None:
    try:
        settings.validate()
    except (ValueError, FileNotFoundError) as exc:
        logging.critical("Configuration error: %s", exc)
        sys.exit(1)

    OrchestratorAgent().run()


if __name__ == "__main__":
    main()
