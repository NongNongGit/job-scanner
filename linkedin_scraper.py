import requests
from bs4 import BeautifulSoup
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]


def scrape_linkedin_jobs(keyword, location, remote_only=False, contract_only=False):
    url = (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={keyword.replace(' ', '%20')}"
        f"&location={location.replace(' ', '%20')}"
        "&f_TPR=r86400"  # last 24 hours
    )

    headers = {"User-Agent": random.choice(USER_AGENTS)}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for job in soup.select(".base-card"):
        title = job.select_one(".base-card__full-link")
        company = job.select_one(".base-card__subtitle")
        link = title["href"] if title else None
        location_text = job.select_one(".job-search-card__location")

        if not title or not company:
            continue

        title_text = title.get_text(strip=True)
        company_text = company.get_text(strip=True)
        location_text = location_text.get_text(strip=True) if location_text else ""

        # Remote filter
        if (
            remote_only
            and "remote" not in title_text.lower()
            and "remote" not in location_text.lower()
        ):
            continue

        # Contract filter
        if contract_only and "contract" not in title_text.lower():
            continue

        results.append(
            {
                "title": title_text,
                "company": company_text,
                "location": location_text,
                "link": link,
                "source": "LinkedIn",
                "keyword": keyword,
                "region": location,
            }
        )

    time.sleep(1)  # polite delay
    return results
