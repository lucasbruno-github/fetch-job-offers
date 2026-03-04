"""Scrapes job listings from LinkedIn's public (no-auth) guest job search API."""

import logging
import random
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from ..models.schemas import JobOffer

logger = logging.getLogger(__name__)

_SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
_DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def fetch_jobs(
    query: str,
    location: str = "",
    hours_old: int = 24,
    max_results: int = 10,
) -> list[JobOffer]:
    """
    Fetch job listings from LinkedIn's public job search.

    Args:
        query: Job title / keywords (e.g. "Data Scientist")
        location: Location filter (e.g. "France"). Empty = worldwide.
        hours_old: Only return jobs posted within the last N hours.
        max_results: Maximum number of jobs to return.

    Returns:
        List of JobOffer dicts with full descriptions.
    """
    params = {
        "keywords": query,
        "location": location,
        "f_TPR": f"r{hours_old * 3600}",  # r86400 = last 24 hours
        "start": 0,
        "count": max_results,
    }

    logger.info("Fetching LinkedIn jobs: query=%r location=%r hours_old=%d", query, location, hours_old)

    try:
        resp = requests.get(_SEARCH_URL, headers=_HEADERS, params=params, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("LinkedIn search request failed: %s", exc)
        raise

    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.find_all("div", class_="base-card")
    logger.info("Found %d job cards on the search page.", len(cards))

    jobs: list[JobOffer] = []
    for card in cards[:max_results]:
        job = _parse_card(card)
        if job is None:
            continue

        # Polite delay between detail requests
        time.sleep(random.uniform(1.0, 2.5))
        job["description"] = _fetch_description(job["job_id"])
        jobs.append(job)
        logger.info("Fetched: %s @ %s", job["title"], job["company"])

    return jobs


def _parse_card(card) -> Optional[JobOffer]:
    """Extract structured data from a LinkedIn job card HTML element."""
    urn: str = card.get("data-entity-urn", "")
    job_id = urn.split(":")[-1] if "jobPosting" in urn else ""
    if not job_id:
        return None

    title_el = card.find("h3", class_="base-search-card__title")
    company_el = card.find("h4", class_="base-search-card__subtitle")
    location_el = card.find("span", class_="job-search-card__location")
    link_el = card.find("a", class_="base-card__full-link")

    return JobOffer(
        job_id=job_id,
        title=title_el.get_text(strip=True) if title_el else "Unknown Title",
        company=company_el.get_text(strip=True) if company_el else "Unknown Company",
        location=location_el.get_text(strip=True) if location_el else "",
        url=(
            link_el["href"].split("?")[0]
            if link_el
            else f"https://www.linkedin.com/jobs/view/{job_id}"
        ),
        description="",
    )


def _fetch_description(job_id: str) -> str:
    """Fetch the full job description from the LinkedIn job detail page."""
    url = _DETAIL_URL.format(job_id)
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Could not fetch description for job %s: %s", job_id, exc)
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    # Try multiple CSS selectors — LinkedIn occasionally changes its markup
    for tag, css_class in [
        ("div", "show-more-less-html__markup"),
        ("div", "description__text"),
        ("section", "description"),
    ]:
        el = soup.find(tag, class_=css_class)
        if el:
            return el.get_text(separator="\n", strip=True)

    logger.warning("Description element not found for job %s.", job_id)
    return ""
