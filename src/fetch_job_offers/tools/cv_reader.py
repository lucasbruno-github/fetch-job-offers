"""Reads user-provided files from the project root."""

import logging
from ..config import settings

logger = logging.getLogger(__name__)


def read_cv() -> str:
    """Return the full text of the user's CV (cv.md)."""
    text = settings.CV_PATH.read_text(encoding="utf-8").strip()
    logger.info("CV loaded: %d characters.", len(text))
    return text


def read_template() -> str:
    """Return the cover letter template (cover_letter_template.md)."""
    text = settings.TEMPLATE_PATH.read_text(encoding="utf-8").strip()
    logger.info("Template loaded: %d characters.", len(text))
    return text
