"""
Cover Letter Sub-Agent

Generates a personalized cover letter by adapting a user-provided template
to a specific job offer and candidate CV.
Uses Gemini 2.0 Flash as a single-turn generation.
"""

import logging

from google import genai
from google.genai import types

from ..config import settings
from ..models.schemas import JobOffer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt — tuned for concise, concrete, template-faithful output
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """
You are a professional career coach specialized in data science job applications.

Your task: Write a personalized cover letter by adapting the provided template to the specific job and candidate.

Rules:
1. Follow the template's structure and section order exactly — do not add or remove sections.
2. Replace every placeholder or generic section with specific, job-relevant content.
3. Reference at least 2 concrete examples from the CV that directly match stated job requirements.
4. Never use vague filler phrases such as "passionate about", "team player", "hard worker", "I believe I would be a great fit".
5. Keep the total length around the template's length.
6. Each paragraph must serve a clear, distinct purpose (hook → evidence → evidence → close).
7. Tone: confident and direct — professional but not stiff. Match the seniority level of the role.
8. Do NOT add a subject line, date, address block, or any metadata unless the template includes them.

Output: Only the cover letter body text — no title, no preamble, no explanation.
""".strip()


class CoverLetterAgent:
    """Single-turn Gemini agent that generates a personalized cover letter."""

    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._config = types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
        )

    def write(self, job: JobOffer, cv_text: str, template: str) -> str:
        """
        Generate a personalized cover letter for the given job.

        Args:
            job: The job offer to apply for.
            cv_text: The full text of the candidate's CV.
            template: The user's preferred cover letter template (markdown).

        Returns:
            The full cover letter as a plain text string.
        """
        prompt = (
            f"**Job Title:** {job['title']}\n"
            f"**Company:** {job['company']}\n"
            f"**Location:** {job['location']}\n\n"
            f"### Job Description\n{job['description']}\n\n"
            f"### Candidate CV\n{cv_text}\n\n"
            f"### Cover Letter Template to Adapt\n{template}"
        )

        logger.info("Generating cover letter for: %s @ %s", job["title"], job["company"])
        response = self._client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=self._config,
        )
        return response.text.strip()
