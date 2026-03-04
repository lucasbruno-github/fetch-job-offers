"""
CV Analyzer Sub-Agent

Analyzes the correspondence between a candidate's CV and a job description.
Uses Gemini 2.0 Flash as a single-turn generation (no tool use needed here).
"""

import logging

from google import genai
from google.genai import types

from ..config import settings
from ..models.schemas import JobOffer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt — tuned for structured, actionable output
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """
You are a senior technical recruiter specializing in data science, machine learning, and AI positions.

Your task: Given a job description and a candidate's CV, produce a concise, structured skills match analysis.

Output format — use EXACTLY this markdown structure:

## Skills Match Analysis

### ✅ Skills You Have
- **[skill]** — [one sentence: how/where it appears in the CV]
(list only skills explicitly required in the job description AND clearly present in the CV)

### ❌ Skills You're Missing
- **[skill]** — [one sentence: why it matters for this specific role]
(list only skills explicitly required in the job description AND absent from the CV)

### 📊 Overall Match
[2–3 sentences: estimated fit percentage, top 2 strengths the candidate brings, top 1–2 gaps to address. Be specific and actionable — no generic advice.]

Rules:
- Only reference skills explicitly stated in the job description (not inferred).
- Only mark a skill as "have" if it is explicitly stated in the CV (not assumed from experience).
- Keep each list to a maximum of 6 items.
- Never repeat information between sections.
- Respond ONLY with the structured analysis — no preamble, no sign-off.
""".strip()


class CVAnalyzerAgent:
    """Single-turn Gemini agent that analyses CV/job correspondence."""

    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._config = types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
        )

    def analyze(self, job: JobOffer, cv_text: str) -> str:
        """
        Return a markdown skills match analysis for the given job and CV.

        Args:
            job: The job offer to evaluate.
            cv_text: The full text of the candidate's CV.

        Returns:
            Markdown-formatted analysis string.
        """
        prompt = (
            f"**Job Title:** {job['title']}\n"
            f"**Company:** {job['company']}\n"
            f"**Location:** {job['location']}\n\n"
            f"### Job Description\n{job['description']}\n\n"
            f"### Candidate CV\n{cv_text}"
        )

        logger.info("Analyzing CV match for: %s @ %s", job["title"], job["company"])
        response = self._client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=self._config,
        )
        return response.text.strip()
