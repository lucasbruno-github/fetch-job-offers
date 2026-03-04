"""
fetch-job-offers — CLI entry point.

Usage:
    uv run python main.py                          # run with .env defaults
    uv run python main.py --query "ML Engineer"    # override search query
    uv run python main.py --location "France" --max-jobs 3
    uv run python main.py --help

First-time setup:
    uv run python setup.py
"""

import logging
import sys
from typing import Optional

import typer

# Configure logging before importing project modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)

from fetch_job_offers.agents.orchestrator import OrchestratorAgent
from fetch_job_offers.config import settings

app = typer.Typer(
    name="fetch-job-offers",
    help="Fetch Data Scientist job offers from LinkedIn and receive a personalised digest by email.",
    add_completion=False,
)


@app.command()
def run(
    query: Optional[str] = typer.Option(
        None, "--query", "-q",
        help="Job search query. Overrides SEARCH_QUERY from .env.",
        show_default=False,
    ),
    location: Optional[str] = typer.Option(
        None, "--location", "-l",
        help="Location filter (e.g. 'France', 'Paris'). Empty = worldwide.",
        show_default=False,
    ),
    max_jobs: Optional[int] = typer.Option(
        None, "--max-jobs", "-n",
        help="Maximum number of job offers to process. Overrides MAX_JOBS from .env.",
        min=1, max=20,
        show_default=False,
    ),
    hours: Optional[int] = typer.Option(
        None, "--hours",
        help="Lookback window in hours. Overrides HOURS_OLD from .env.",
        min=1, max=168,
        show_default=False,
    ),
    model: Optional[str] = typer.Option(
        None, "--model",
        help="Gemini model to use (e.g. 'gemini-1.5-flash'). Overrides GEMINI_MODEL from .env.",
        show_default=False,
    ),
) -> None:
    """Run the full job digest pipeline."""
    # Validate config (credentials + required files)
    try:
        settings.validate()
    except (ValueError, FileNotFoundError) as exc:
        typer.echo(f"❌  Configuration error: {exc}", err=True)
        typer.echo("   Run 'uv run python setup.py' to configure the project.", err=True)
        raise typer.Exit(code=1)

    # Apply CLI overrides on top of .env values
    if query is not None:
        settings.SEARCH_QUERY = query
    if location is not None:
        settings.LINKEDIN_LOCATION = location
    if max_jobs is not None:
        settings.MAX_JOBS = max_jobs
    if hours is not None:
        settings.HOURS_OLD = hours
    if model is not None:
        settings.GEMINI_MODEL = model

    typer.echo(
        f"🔍  Searching: '{settings.SEARCH_QUERY}'"
        f"{f' in {settings.LINKEDIN_LOCATION}' if settings.LINKEDIN_LOCATION else ' (worldwide)'}"
        f" — last {settings.HOURS_OLD}h — up to {settings.MAX_JOBS} offers"
    )

    OrchestratorAgent().run()


if __name__ == "__main__":
    app()
