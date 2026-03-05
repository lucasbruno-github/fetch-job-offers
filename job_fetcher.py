import pandas as pd
import openpyxl

from fetch_job_offers.config import settings
from fetch_job_offers.tools import linkedin_scraper


raw_jobs = linkedin_scraper.fetch_jobs(
    query=settings.SEARCH_QUERY,
    location=settings.LINKEDIN_LOCATION,
    hours_old=settings.HOURS_OLD,
    max_results=settings.MAX_JOBS * 2,
)

print(len(raw_jobs))

ids = [job["job_id"] for job in raw_jobs]
titles = [job["title"] for job in raw_jobs]
companies = [job["company"] for job in raw_jobs]
urls = [job["url"] for job in raw_jobs]

df_jobs = pd.DataFrame({"job_id": ids, "title": titles, "company": companies, "url": urls})

df_jobs.to_excel("linkedin_jobs.xlsx", index=False)

print(urls)


print(settings.MAX_JOBS)
print(len(df_jobs))


print(len(ids))
