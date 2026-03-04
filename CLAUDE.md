# fetch_job_offers — Project Guide

## Purpose
A manually-triggered Python script that:
1. Fetches the top 5 Data Scientist job offers from LinkedIn (last 24 hours)
2. Analyzes each offer against the user's CV (skills match / gap)
3. Generates a tailored cover letter per offer based on a user-provided template
4. Sends everything in a single digest email

## Architecture

```
fetch_job_offers/
├── main.py                      # Entry point — run this manually
├── fetcher.py                   # LinkedIn scraping via python-jobspy
├── cv_parser.py                 # Reads cv.md
├── analyzer.py                  # Gemini 2.0 Flash: skills match/gap analysis
├── cover_letter.py              # Gemini 2.0 Flash: cover letter generation
├── emailer.py                   # Gmail SMTP digest sender
├── cv.md                        # [USER-PROVIDED] CV in Markdown format
├── cover_letter_template.md     # [USER-PROVIDED] Cover letter template
├── seen_jobs.json               # Auto-generated: deduplication tracker
├── .env                         # [USER-PROVIDED] Secrets (never commit)
└── pyproject.toml
```

## Tech Stack
- **Job scraping**: `python-jobspy` — scrapes public LinkedIn job pages, no auth needed
- **LLM**: Google Gemini 2.0 Flash API (free tier: 15 req/min, 1M tokens/day)
- **Email**: `smtplib` + Gmail SMTP (stdlib, no extra lib)
- **Config**: `python-dotenv` — loads `.env` at runtime
- **Package manager**: `uv`

## Module Responsibilities
| File | Role |
|---|---|
| `fetcher.py` | Search LinkedIn for "Data Scientist", last 24h, return top 5 new jobs |
| `cv_parser.py` | Read and return raw text from `cv.md` |
| `analyzer.py` | Call Gemini to compare a job description against the CV |
| `cover_letter.py` | Call Gemini to fill the cover letter template for a specific job |
| `emailer.py` | Compose and send the HTML/text digest email |
| `main.py` | Orchestrate the pipeline: fetch → parse → analyze → cover letter → email |

## User-Provided Files

### `.env`
```
GEMINI_API_KEY=your_gemini_api_key
GMAIL_USER=you@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
RECIPIENT_EMAIL=you@gmail.com
```
> Gmail App Password: Google Account → Security → 2-Step Verification → App Passwords

### `cv.md`
Your full CV in Markdown format. Place it in the project root.

### `cover_letter_template.md`
Your preferred cover letter structure. Use natural language placeholders — the LLM will
fill them in contextually. Example:
```
Dear Hiring Manager,

I am writing to apply for the [JOB TITLE] position at [COMPANY].

[WHY THIS COMPANY — 1-2 sentences specific to them]

[RELEVANT EXPERIENCE — 2 paragraphs]

[CLOSING SENTENCE]

Sincerely,
[YOUR NAME]
```

## Deduplication
`seen_jobs.json` stores job IDs already sent. On each run, only new jobs are processed.
Delete this file to re-send all offers (useful for testing).

## Key Implementation Rule
**For every structural decision or ambiguity encountered during development** (API
changes, unexpected data shapes, format choices, errors), **stop and ask the user
for guidance or a choice** before proceeding autonomously.

## Running the Script
```bash
uv run python main.py
```
Or with the venv activated:
```bash
python main.py
```
