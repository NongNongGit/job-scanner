import os, json, time, requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from linkedin_scraper import scrape_linkedin_jobs
from job_history import filter_new_jobs
from career_ops_apply import auto_apply
from cv_scoring import score_job

load_dotenv()


def retry(func, retries=3, delay=5):
    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
    return []


KEYWORDS = ["AI Engineer", "Backend Developer", "C# Developer", "Fullstack Developer", ".net developer", "Software Engineer", "Software Developer"]
# Updated location rules
SEARCH_LOCATIONS = [
    {
        "name": "Auckland",
        "geo_id": "102393603",
        "remote_only": False,
        "contract_only": False,
    },
    {
        "name": "Australia",
        "geo_id": "101452733",
        "remote_only": True,
        "contract_only": False,
    },
    {
        "name": "Seattle",
        "geo_id": "103644278",
        "remote_only": True,
        "contract_only": False,
    },
    {
        "name": "United Kingdom",
        "geo_id": "101165590",
        "remote_only": True,
        "contract_only": False,
    },
]

REMOTE_FILTERS = ["Remote", "Hybrid"]
CONTRACT_KEYWORDS = ["Contract", "Contractor", "Temp", "Temporary"]


def is_senior_role(title):
    title_lower = title.lower()
    senior_keywords = [
        "senior",
        "staff",
    ]
    return any(k in title_lower for k in senior_keywords)


# -----------------------------
# LINKEDIN API
# -----------------------------
def fetch_linkedin_jobs():
    jobs = []

    for kw in KEYWORDS:
        for loc in SEARCH_LOCATIONS:
            results = scrape_linkedin_jobs(
                keyword=kw,
                location=loc["name"],
                remote_only=loc["remote_only"],
                contract_only=loc["contract_only"],
            )
            jobs.extend(results)

    return jobs


# -----------------------------
# SEEK API
# -----------------------------
def fetch_seek_jobs():
    url = "https://www.seek.co.nz/api/jobs"
    jobs = []

    for kw in KEYWORDS:
        for loc in SEARCH_LOCATIONS:

            params = {"keywords": kw, "location": loc["name"]}

            # Remote only
            if loc["remote_only"]:
                params["workType"] = "remote"

            r = requests.get(url, params=params)
            if r.status_code != 200:
                continue

            for job in r.json().get("jobs", []):
                title = job.get("title", "")

                # Contract filter
                if loc["contract_only"] and not any(
                    ck.lower() in title.lower() for ck in CONTRACT_KEYWORDS
                ):
                    continue

                jobs.append(
                    {
                        "title": job.get("title"),
                        "company": job.get("advertiser", {}).get("name"),
                        "location": job.get("location"),
                        "link": job.get("link"),
                        "source": "Seek",
                        "keyword": kw,
                        "region": loc["name"],
                    }
                )

    return jobs


# -----------------------------
# EMAIL RESULTS
# -----------------------------
def send_email(jobs):
    html = f"<h3>Daily Job Scan Results</h3><p>Total jobs found: {len(jobs)}</p>"

    for job in jobs:
        html += f"""
        <p>
            <b>{job['title']}</b> — {job['company']}<br>
            {job['location']} ({job['region']})<br>
            <a href="{job['link']}">Apply</a><br>
            Source: {job['source']}
        </p>
        """

    message = Mail(
        from_email="nongnong55b@gmail.com",
        to_emails="nongnong55b@gmail.com",
        subject="Daily Job Scan Results",
        html_content=html,
    )

    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    sg.send(message)


# -----------------------------
# MAIN
# -----------------------------
def main():
    linkedin_jobs = fetch_linkedin_jobs()
    seek_jobs = fetch_seek_jobs()
    all_jobs = linkedin_jobs + seek_jobs

    # Track history
    new_jobs = filter_new_jobs(all_jobs)

    # Senior-only filter
    senior_jobs = [job for job in new_jobs if is_senior_role(job["title"])]

    # Add CV score
    for job in senior_jobs:
        job["cv_score"] = score_job(job.get("description", ""))

    # Filter by score (optional)
    scored_jobs = [job for job in senior_jobs if job["cv_score"] >= 4]

    # Save scored jobs
    with open("jobs.json", "w") as f:
        json.dump(scored_jobs, f, indent=2)

    # Career-Ops assisted apply (prepare only)
    for job in scored_jobs:
        auto_apply(job)

    # Email summary
    if scored_jobs:
        send_email(scored_jobs)


if __name__ == "__main__":
    main()
