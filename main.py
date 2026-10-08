import os, json, datetime, requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

KEYWORDS = ["AI Engineer", "Backend Developer", "C# Developer", "Fullstack Developer"]

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
        "contract_only": True,
    },
    {
        "name": "Seattle",
        "geo_id": "103644278",
        "remote_only": True,
        "contract_only": True,
    },
    {
        "name": "United Kingdom",
        "geo_id": "101165590",
        "remote_only": True,
        "contract_only": True,
    },
]

REMOTE_FILTERS = ["Remote", "Hybrid"]
CONTRACT_KEYWORDS = ["Contract", "Contractor", "Temp", "Temporary"]


# -----------------------------
# LINKEDIN API
# -----------------------------
def fetch_linkedin_jobs():
    url = "https://linkedin-jobs-api.p.rapidapi.com/search"
    headers = {"X-RapidAPI-Key": os.getenv("RAPID_API_KEY")}
    jobs = []

    for kw in KEYWORDS:
        for loc in SEARCH_LOCATIONS:
            params = {"keywords": kw, "geo_id": loc["geo_id"], "limit": 20}

            r = requests.get(url, headers=headers, params=params)
            if r.status_code != 200:
                continue

            for job in r.json().get("data", []):
                workplace = job.get("workplaceType", "")
                title = job.get("title", "")

                # Remote filter
                if loc["remote_only"] and not any(
                    rf in workplace for rf in REMOTE_FILTERS
                ):
                    continue

                # Contract filter
                if loc["contract_only"] and not any(
                    ck.lower() in title.lower() for ck in CONTRACT_KEYWORDS
                ):
                    continue

                jobs.append(
                    {
                        "title": job.get("title"),
                        "company": job.get("companyName"),
                        "location": job.get("location"),
                        "link": job.get("applyUrl"),
                        "source": "LinkedIn",
                        "keyword": kw,
                        "region": loc["name"],
                    }
                )

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

    # Save results
    with open("jobs.json", "w") as f:
        json.dump(all_jobs, f, indent=2)

    # Email summary
    send_email(all_jobs)


if __name__ == "__main__":
    main()
