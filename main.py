import os, json, datetime, requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def fetch_linkedin_jobs():
    url = "https://linkedin-jobs-api.p.rapidapi.com/search"
    headers = {"X-RapidAPI-Key": os.getenv("RAPID_API_KEY")}
    keywords = [
        "fullstack developer",
        "AI Developer",
        "Backend Developer",
    ]
    jobs = []
    for kw in keywords:
        params = {"keywords": kw, "geo_id": "92000000", "limit": 10}
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
            for job in r.json().get("data", []):
                if "Remote" in job.get("workplaceType", "") or "Hybrid" in job.get(
                    "workplaceType", ""
                ):
                    jobs.append(
                        {
                            "title": job.get("title"),
                            "company": job.get("companyName"),
                            "location": job.get("location"),
                            "link": job.get("applyUrl"),
                            "source": "LinkedIn",
                        }
                    )
    return jobs


def fetch_seek_jobs():
    url = "https://www.seek.co.nz/api/jobs"
    keywords = [
        "fullstack developer",
        "AI Developer",
        "Backend Developer",
    ]
    jobs = []
    for kw in keywords:
        params = {"keywords": kw, "location": "New Zealand", "workType": "remote"}
        r = requests.get(url, params=params)
        if r.status_code == 200:
            for job in r.json().get("jobs", []):
                jobs.append(
                    {
                        "title": job.get("title"),
                        "company": job.get("advertiser", {}).get("name"),
                        "location": job.get("location"),
                        "link": job.get("link"),
                        "source": "Seek",
                    }
                )
    return jobs


def send_email(jobs):
    message = Mail(
        from_email="you@example.com",
        to_emails="you@example.com",
        subject="Daily Job Scan Results",
        html_content=f"<p>Found {len(jobs)} new jobs today.</p>",
    )
    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    sg.send(message)


def main():
    linkedin_jobs = fetch_linkedin_jobs()
    seek_jobs = fetch_seek_jobs()
    all_jobs = linkedin_jobs + seek_jobs
    with open("jobs.json", "w") as f:
        json.dump(all_jobs, f, indent=2)
    send_email(all_jobs)


if __name__ == "__main__":
    main()
