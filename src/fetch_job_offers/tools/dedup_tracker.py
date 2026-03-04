"""Tracks job IDs that have already been sent to avoid re-sending duplicates."""

import json
import logging
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)


def _load() -> set[str]:
    path: Path = settings.SEEN_JOBS_PATH
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return set(data) if isinstance(data, list) else set()
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not read seen_jobs.json, starting fresh: %s", e)
        return set()


def _save(seen: set[str]) -> None:
    settings.SEEN_JOBS_PATH.write_text(
        json.dumps(sorted(seen), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def is_new(job_id: str) -> bool:
    """Return True if this job_id has not been sent yet."""
    return job_id not in _load()


def mark_seen(job_ids: list[str]) -> None:
    """Persist a list of job IDs as already sent."""
    seen = _load()
    seen.update(job_ids)
    _save(seen)
    logger.info("Marked %d job(s) as seen.", len(job_ids))


def filter_new(jobs: list[dict]) -> list[dict]:
    """Return only jobs whose job_id has not been seen before."""
    seen = _load()
    return [j for j in jobs if j.get("job_id") not in seen]
