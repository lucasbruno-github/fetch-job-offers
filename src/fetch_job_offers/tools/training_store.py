"""
Training data store — appends LLM interactions to a JSONL file.

Each record captures the exact system prompt, user prompt, and model output
for one agent call, in the standard chat format used by most fine-tuning
frameworks (OpenAI, HuggingFace, Axolotl, etc.).

Output file: outputs/training_data.jsonl  (one JSON object per line)
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from ..config import BASE_DIR

logger = logging.getLogger(__name__)

_OUTPUT_DIR = BASE_DIR / "outputs"
_JSONL_PATH = _OUTPUT_DIR / "training_data.jsonl"


def append(
    agent: str,
    job_id: str,
    job_title: str,
    company: str,
    system_prompt: str,
    user_prompt: str,
    output: str,
) -> None:
    """
    Append one training example to outputs/training_data.jsonl.

    The record format mirrors the standard chat fine-tuning schema:
    {
        "agent":     "cv_analyzer" | "cover_letter",
        "job_id":    "123456789",
        "title":     "Data Scientist",
        "company":   "Acme Corp",
        "timestamp": "2026-03-05T10:00:00+00:00",
        "messages": [
            {"role": "system",    "content": "<system prompt>"},
            {"role": "user",      "content": "<user prompt>"},
            {"role": "assistant", "content": "<model output>"}
        ]
    }

    Args:
        agent:         Name of the calling agent ("cv_analyzer" or "cover_letter").
        job_id:        LinkedIn job ID for traceability.
        job_title:     Job title.
        company:       Company name.
        system_prompt: The exact system instruction sent to the model.
        user_prompt:   The exact user message sent to the model.
        output:        The raw text returned by the model.
    """
    _OUTPUT_DIR.mkdir(exist_ok=True)

    record = {
        "agent": agent,
        "job_id": job_id,
        "title": job_title,
        "company": company,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": output},
        ],
    }

    with _JSONL_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.debug("Training record appended: %s / %s @ %s", agent, job_title, company)
