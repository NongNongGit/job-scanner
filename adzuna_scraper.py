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

    # Pick the first keyword and sanitize it
    keyword = keywords[0].replace("#", "").replace(".", "").lower()

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 50,
        "what": keyword,
        "where": location,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        jobs = []
        for item in data.get("results", []):
            jobs.append(
                {
                    "title": item.get("title"),
                    "company": item.get("company", {}).get("display_name"),
                    "location": item.get("location", {}).get("display_name"),
                    "url": item.get("redirect_url"),
                    "description": item.get("description"),
                    "source": "adzuna",
                }
            )
        return jobs

    except Exception as e:
        print("Adzuna error:", e)
        return []
