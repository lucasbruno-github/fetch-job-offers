"""
Pipeline orchestrator — plain Python, no LLM coordination needed.

The pipeline is fully sequential and deterministic, so a simple Python
class is the right level of complexity here. The LLM intelligence lives
exclusively in CVAnalyzerAgent and CoverLetterAgent.

Steps:
  1. Fetch jobs from LinkedIn, filter already-seen ones
  2. Read CV and cover letter template
  3. For each job: analyze CV match, then generate cover letter
  4. Send the email digest (or a no-jobs notification)
"""

import logging

from ..config import settings
from ..models.schemas import DigestItem
from ..tools import cv_reader, dedup_tracker, email_tool, linkedin_scraper
from .cover_letter_agent import CoverLetterAgent
from .cv_analyzer_agent import CVAnalyzerAgent

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Runs the full job digest pipeline end-to-end."""

    def __init__(self) -> None:
        self._cv_analyzer = CVAnalyzerAgent()
        self._cover_letter_agent = CoverLetterAgent()

    def run(self) -> None:
        """Execute the pipeline: fetch → analyze → generate → send."""
        # --- 1. Load user files ---
        cv_text = cv_reader.read_cv()
        template = cv_reader.read_template()

        # --- 2. Fetch and deduplicate jobs ---
        raw_jobs = linkedin_scraper.fetch_jobs(
            query=settings.SEARCH_QUERY,
            location=settings.LINKEDIN_LOCATION,
            hours_old=settings.HOURS_OLD,
            max_results=settings.MAX_JOBS * 2,
        )
        jobs = dedup_tracker.filter_new(raw_jobs)[: settings.MAX_JOBS]
        logger.info("%d new job(s) to process.", len(jobs))

        if not jobs:
            email_tool.send_no_jobs_notification()
            logger.info("No new jobs — notification email sent.")
            return

        # --- 3. Analyze + cover letter for each job ---
        items: list[DigestItem] = []
        for job in jobs:
            logger.info("Processing: %s @ %s", job["title"], job["company"])
            analysis = self._cv_analyzer.analyze(job, cv_text)
            cover_letter = self._cover_letter_agent.write(job, cv_text, template)
            items.append(DigestItem(job=job, analysis=analysis, cover_letter=cover_letter))

        # --- 4. Send digest and mark jobs as seen ---
        email_tool.send_digest(items)
        dedup_tracker.mark_seen([j["job_id"] for j in jobs])
        logger.info("Pipeline complete — digest sent with %d offer(s).", len(items))
