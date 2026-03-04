# fetch-job-offers

Fetches the top 5 Data Scientist job offers posted on LinkedIn in the last 24 hours, analyzes each one against your CV, generates a personalized cover letter, and sends everything to your inbox in a single digest email.

## How it works

1. **Scrapes LinkedIn** public job search (no account needed) for recent offers matching your query
2. **Analyzes each offer** against your CV — highlights skills you have and skills you're missing
3. **Writes a cover letter** per offer, adapted from your personal template
4. **Sends a digest email** with all results
5. **Remembers what was sent** — won't send the same offer twice

---

## Prerequisites

- [Python 3.13+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- A [Google Gemini API key](https://aistudio.google.com) (free tier)
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords)

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/lucasbruno-github/fetch-job-offers.git
cd fetch-job-offers

# 2. Install dependencies
uv sync
```

---

## Setup (first time)

Run the interactive wizard — it will guide you through every step:

```bash
uv run python setup.py
```

The wizard will:
- Ask for your credentials and save them to `.env`
- Create a `cv.md` stub if you don't have one yet
- Create a `cover_letter_template.md` stub if you don't have one yet

### Manual setup (alternative)

If you prefer to configure manually, create a `.env` file at the project root:

```dotenv
# ── Gemini API ──────────────────────────────────────────────
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GEMINI_MODEL=gemini-2.5-flash          # optional, this is the default

# ── Email (Gmail SMTP) ──────────────────────────────────────
GMAIL_USER=yourname@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop  # 16-char App Password, spaces OK
RECIPIENT_EMAIL=yourname@gmail.com      # where to receive the digest

# ── LinkedIn search parameters ──────────────────────────────
SEARCH_QUERY=Data Scientist             # optional, this is the default
LINKEDIN_LOCATION=France                # optional, leave empty for worldwide
MAX_JOBS=5                              # optional, default 5 (max 20)
HOURS_OLD=24                            # optional, default 24
```

> ⚠️ The `.env` file contains secrets — it is gitignored and must **never** be committed.

#### How to get a Gmail App Password

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required)
3. Search for **App Passwords**
4. Create a password for "Mail" → copy the 16-character code
5. Paste it into `GMAIL_APP_PASSWORD` (spaces are fine)

---

## User files

Place these two files at the project root before running:

### `cv.md` — your CV in Markdown

```markdown
# Jane Doe

## Contact
- Email: jane@example.com
- LinkedIn: linkedin.com/in/janedoe

## Summary
Data Scientist with 4 years of experience in NLP and time-series forecasting.

## Experience

### Data Scientist — Acme Corp (2021 – present)
- Built a churn prediction model (XGBoost) reducing churn by 18%
- Deployed ML pipelines on AWS SageMaker serving 2M daily predictions

## Skills
- **Languages:** Python, SQL
- **ML/AI:** scikit-learn, PyTorch, HuggingFace Transformers
- **Cloud:** AWS (SageMaker, S3, Lambda), GCP (BigQuery)
- **Tools:** Git, Docker, Airflow, dbt

## Education
### MSc Data Science — Université Paris-Saclay (2021)
```

### `cover_letter_template.md` — your cover letter structure

The LLM will adapt this template to each specific job. Use natural language sections — no rigid placeholders needed.

```markdown
Dear Hiring Manager,

[Opening: one specific reason you're interested in THIS company — reference something concrete about their product, mission, or recent work]

[First body paragraph: your most relevant experience that directly matches the role's core technical requirement — be specific, cite numbers where possible]

[Second body paragraph: a second concrete achievement that addresses another key requirement from the job description]

[Closing: confident call to action, no generic "I look forward to hearing from you"]

Sincerely,
Jane Doe
```

---

## Running the pipeline

```bash
# Default run (uses .env settings)
uv run python main.py

# Override search parameters for a specific run
uv run python main.py --query "Machine Learning Engineer" --location "Paris"
uv run python main.py --query "NLP Engineer" --max-jobs 3 --hours 48
uv run python main.py --model "gemini-1.5-flash"

# See all options
uv run python main.py --help
```

### CLI options

| Option | Short | Description | Default |
|---|---|---|---|
| `--query` | `-q` | Job search query | `SEARCH_QUERY` from `.env` |
| `--location` | `-l` | Location filter (`"France"`, `"Paris"`, …) | `LINKEDIN_LOCATION` from `.env` |
| `--max-jobs` | `-n` | Max offers to process (1–20) | `MAX_JOBS` from `.env` |
| `--hours` | | Lookback window in hours (1–168) | `HOURS_OLD` from `.env` |
| `--model` | | Gemini model override | `GEMINI_MODEL` from `.env` |

CLI options always take precedence over `.env` values for that run only — `.env` is never modified.

---

## Project structure

```
fetch-job-offers/
├── main.py                        # Entry point (CLI)
├── setup.py                       # First-time setup wizard
├── cv.md                          # Your CV — fill this in (gitignored)
├── cover_letter_template.md       # Your template — fill this in (gitignored)
├── .env                           # Your secrets — never commit (gitignored)
├── seen_jobs.json                 # Auto-generated deduplication log (gitignored)
└── src/
    └── fetch_job_offers/
        ├── config.py              # Settings loader
        ├── models/schemas.py      # Data types
        ├── tools/
        │   ├── linkedin_scraper.py  # LinkedIn public job search
        │   ├── cv_reader.py         # Reads cv.md and template
        │   ├── dedup_tracker.py     # seen_jobs.json management
        │   └── email_tool.py        # Gmail SMTP sender
        └── agents/
            ├── cv_analyzer_agent.py     # Gemini: skills match analysis
            ├── cover_letter_agent.py    # Gemini: cover letter generation
            └── orchestrator.py          # Pipeline coordinator
```

---

## Deduplication

`seen_jobs.json` keeps track of job IDs already sent. On each run, only new offers are processed. To reset and re-process all offers (useful for testing), delete the file:

```bash
rm seen_jobs.json
```

---

## Free tier limits

| Service | Free quota |
|---|---|
| Gemini 2.5 Flash | Check [ai.google.dev/gemini-api/docs/rate-limits](https://ai.google.dev/gemini-api/docs/rate-limits) |
| Gmail SMTP | 500 emails/day |
| LinkedIn scraping | No official limit — one run/day is safe |

A typical run (5 offers) makes ~10 Gemini API calls (1 analysis + 1 cover letter per offer). Well within the free tier for a daily run.

---

## Troubleshooting

**`FileNotFoundError: CV file not found`**
→ Create `cv.md` in the project root, or run `uv run python setup.py`.

**`429 RESOURCE_EXHAUSTED` (Gemini)**
→ Your model may not be on the free tier. Try `--model gemini-1.5-flash`.

**`SMTPAuthenticationError` (Gmail)**
→ Make sure you're using an App Password, not your regular Gmail password.

**LinkedIn returns 0 jobs**
→ LinkedIn occasionally blocks scrapers. Wait a few minutes and retry. You can also try a more generic `--query`.
