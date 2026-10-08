import requests
from bs4 import BeautifulSoup
import random
import time


# Rotating user agents to avoid LinkedIn blocking Python requests
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Windows NT 10.0; WOW64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3)",
]

# Optional proxy list (you can add your own)
PROXIES = [
    # Example format:
    # {"http": "http://123.123.123.123:8080", "https": "http://123.123.123.123:8080"}
]


def scrape_linkedin_jobs(keyword, location, remote_only=False, contract_only=False):
    url = (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={keyword.replace(' ', '%20')}"
        f"&location={location.replace(' ', '%20')}"
        "&f_TPR=r86400"  # last 24 hours
    )

    results = []
    max_retries = 5

    for attempt in range(max_retries):
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}

            proxy = random.choice(PROXIES) if PROXIES else None

            response = requests.get(url, headers=headers, proxies=proxy, timeout=10)

            # Retry on rate-limit or temporary block
            if response.status_code in [429, 503, 403]:
                wait = 2**attempt
                print(
                    f"LinkedIn rate-limited (status {response.status_code}). Retrying in {wait}s..."
                )
                time.sleep(wait)
                continue

            if response.status_code != 200:
                print(f"LinkedIn request failed: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, "html.parser")

            for job in soup.select(".base-card"):
                title = job.select_one(".base-card__full-link")
                company = job.select_one(".base-card__subtitle")
                link = title["href"] if title else None
                location_text = job.select_one(".job-search-card__location")

                if not title or not company:
                    continue

                title_text = title.get_text(strip=True)
                company_text = company.get_text(strip=True)
                location_text = (
                    location_text.get_text(strip=True) if location_text else ""
                )
                description = job.get_text(" ", strip=True)

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
                        "description": description,
                    }
                )

            break  # success → stop retrying

        except Exception as e:
            wait = 2**attempt
            print(f"Error scraping LinkedIn: {e}. Retrying in {wait}s...")
            time.sleep(wait)

    # Deduplicate jobs by link
    unique = {job["link"]: job for job in results}
    return list(unique.values())
