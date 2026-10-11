import os
from dotenv import load_dotenv
import requests

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def fetch_adzuna_jobs(profile):
    country = profile["adzuna"]["country"]  # e.g., "nz", "au", "gb", "us"
    keywords = profile["adzuna"]["keywords"]
    location = profile["adzuna"]["location"]

    url = f"{BASE_URL}/{country}/search/1"

    jobs = []
    seen_urls = set()
    for keyword in keywords:
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "results_per_page": 50,
            "what": keyword.replace("#", "").replace(".", "").lower(),
            "where": location,
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            for item in data.get("results", []):
                job = {
                    "title": item.get("title"),
                    "company": item.get("company", {}).get("display_name"),
                    "location": item.get("location", {}).get("display_name"),
                    "url": item.get("redirect_url"),
                    "description": item.get("description"),
                    "source": "adzuna",
                }
                job_url = job["url"]
                if job_url is not None and job_url in seen_urls:
                    continue
                if job_url is not None:
                    seen_urls.add(job_url)
                jobs.append(job)

        except Exception as e:
            print("Adzuna error:", e)

    return jobs
