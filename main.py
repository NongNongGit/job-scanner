import json
import os
from dotenv import load_dotenv

from linkedin_scraper import fetch_linkedin_jobs
from filters import apply_filters
from job_history import filter_new_jobs
from email_sender import send_email, send_summary
from scoring import score_job

load_dotenv()


def load_config():
    # Load global config
    with open("config.json") as f:
        base = json.load(f)

    # Select profile
    profile_name = os.getenv("JOB_PROFILE", "nz")
    profile_path = base["profiles"][profile_name]

    # Load profile config
    with open(f"profiles/{profile_path}") as f:
        profile = json.load(f)

    # Inject global keywords into LinkedIn scraper
    global_kw = base["global_keywords"]
    profile["linkedin"]["keywords"] = global_kw[:]  # copy

    return base, profile


def retry(func, retries, delay, *args):
    import time

    for attempt in range(1, retries + 1):
        try:
            return func(*args)
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
    return []


def main():
    base, profile = load_config()
    retry_cfg = base["retry"]

    # Fetch LinkedIn jobs only
    linkedin_jobs = retry(
        fetch_linkedin_jobs, retry_cfg["retries"], retry_cfg["delay_seconds"], profile
    )

    all_jobs = linkedin_jobs

    # Apply filters
    filtered_jobs = [job for job in all_jobs if apply_filters(job, profile)]

    # Load CV text
    with open("cv.txt") as f:
        cv_text = f.read()

    # Score jobs
    scored_jobs = []
    for job in filtered_jobs:
        job["score"] = score_job(job, cv_text, base, profile)
        scored_jobs.append(job)

    # Filter by minimum score
    min_score = base["scoring"]["min_score_to_email"]
    final_jobs = [j for j in scored_jobs if j["score"] >= min_score]

    # Save output
    with open("jobs.json", "w") as f:
        json.dump(final_jobs, f, indent=2)

    # Send results email
    if final_jobs:
        send_email(final_jobs, base)
    else:
        print("No jobs found — email skipped.")

    # Daily summary
    summary = (
        f"Total jobs fetched: {len(all_jobs)}\n"
        f"After filters: {len(filtered_jobs)}\n"
        f"Above score {min_score}: {len(final_jobs)}"
    )

    send_summary(summary, base)


if __name__ == "__main__":
    main()
