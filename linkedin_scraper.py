import requests
import os


def normalize(value):
    """Convert lists, None, numbers into clean strings."""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if value is None:
        return ""
    return str(value)


def fetch_linkedin_jobs(profile_config):
    keywords = profile_config["linkedin"]["keywords"]
    location = profile_config["linkedin"]["location"]
    job_types = profile_config["linkedin"]["job_types"]
    max_results = profile_config["linkedin"]["max_results"]

    api_key = os.getenv("RAPIDAPI_KEY")

    url = "https://linkedin-job-search-api.p.rapidapi.com/job/search"

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "linkedin-job-search-api.p.rapidapi.com",
    }

    all_jobs = []

    for kw in keywords:
        params = {"keyword": kw, "location": location, "page": 1}

        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            jobs = data.get("data", [])
            for job in jobs:
                clean_job = {
                    "title": normalize(job.get("title")),
                    "company": normalize(job.get("company")),
                    "location": normalize(job.get("location")),
                    "salary": job.get("salary", 0),
                    "url": normalize(job.get("url")),
                    "description": normalize(job.get("description")),
                    "remote": "remote" in normalize(job.get("location")).lower(),
                }

                all_jobs.append(clean_job)

                if len(all_jobs) >= max_results:
                    break

        except Exception as e:
            print(f"LinkedIn API error for keyword '{kw}': {e}")

    return all_jobs
