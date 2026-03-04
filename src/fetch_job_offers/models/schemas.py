"""Shared data schemas for the job digest pipeline."""

from typing import TypedDict


class JobOffer(TypedDict):
    """A job offer fetched from LinkedIn."""
    job_id: str
    title: str
    company: str
    location: str
    url: str
    description: str


class DigestItem(TypedDict):
    """One job entry in the final email digest."""
    job: JobOffer
    analysis: str       # markdown skills match/gap analysis
    cover_letter: str   # personalized cover letter text
