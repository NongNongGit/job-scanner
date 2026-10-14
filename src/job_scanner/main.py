import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

from linkedin_scraper import fetch_linkedin_jobs
from filters import apply_filters
from job_history import filter_new_jobs
from email_sender import send_email, send_summary
from scoring import score_job
from adzuna_scraper import fetch_adzuna_jobs

load_dotenv()


def load_config(config_path="config.json"):
    with open(config_path) as f:
        base = json.load(f)
    return base


def _profile_path(config_path, filename):
    config_dir = Path(config_path).expanduser().resolve().parent
    profile_path = Path(filename).expanduser()
    if profile_path.is_absolute():
        return profile_path
    if profile_path.parent == Path("."):
        # The existing config format stores bare profile names under profiles/.
        return config_dir / "profiles" / profile_path
    return config_dir / profile_path


def load_all_profiles(base, config_path="config.json"):
    profiles = []

    for name, filename in base["profiles"].items():
        with open(_profile_path(config_path, filename)) as f:
            profile = json.load(f)

        # Inject global keywords
        profile["linkedin"]["keywords"] = base["global_keywords"][:]
        profile["adzuna"]["keywords"] = base["global_keywords"][:]

        # Tag profile name for later
        profile["profile_name"] = name

        profiles.append(profile)

    return profiles


def retry(func, retries, delay, *args):
    import time

    for attempt in range(1, retries + 1):
        try:
            return func(*args)
        except Exception as e:
            print("error:", e)
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
    return []


def main(config_path="config.json", cv_path="cv.txt", output_path="jobs.json"):
    base = load_config(config_path)
    profiles = load_all_profiles(base, config_path)
    retry_cfg = base["retry"]

    all_jobs = []

    # Load CV once
    with open(cv_path) as f:
        cv_text = f.read()

    # Loop through all profiles
    for profile in profiles:
        print(f"\n=== Fetching jobs for profile: {profile['profile_name']} ===")

        linkedin_jobs = retry(
            fetch_linkedin_jobs,
            retry_cfg["retries"],
            retry_cfg["delay_seconds"],
            profile,
        )

        # Tag jobs with profile name
        for job in linkedin_jobs:
            job["profile"] = profile["profile_name"]

        # Adzuna jobs
        adzuna_jobs = retry(
            fetch_adzuna_jobs, retry_cfg["retries"], retry_cfg["delay_seconds"], profile
        )

        for job in adzuna_jobs:
            job["profile"] = profile["profile_name"]
            job["source"] = "adzuna"

        combined = linkedin_jobs + adzuna_jobs
        print("combined jobs count:", len(combined))
        # Apply filters
        filtered_jobs = combined  # [job for job in combined if apply_filters(job, profile)]

        # Score jobs
        for job in filtered_jobs:
            job["score"] = score_job(job, cv_text, base, profile)

        all_jobs.extend(filtered_jobs)

    # Filter by minimum score
    min_score = base["scoring"]["min_score_to_email"]
    final_jobs = [j for j in all_jobs if j["score"] >= min_score]

    # Deduplicate by job URL
    dedup = {}
    for job in final_jobs:
        dedup[job["url"]] = job
    final_jobs = list(dedup.values())

    # Save output
    with open(output_path, "w") as f:
        json.dump(final_jobs, f, indent=2)

    # Send results email
    if final_jobs:
        send_email(final_jobs, base)
    else:
        print("No jobs found — email skipped.")

    # Daily summary
    summary = (
        f"Profiles scanned: {len(profiles)}\n"
        f"Total jobs after filters: {len(all_jobs)}\n"
        f"Above score {min_score}: {len(final_jobs)}"
    )

    send_summary(summary, base)


def cli(argv=None):
    parser = argparse.ArgumentParser(
        description="Scan job listings using your configuration, CV, and profiles."
    )
    parser.add_argument(
        "--config", default="config.json", help="path to scanner configuration"
    )
    parser.add_argument("--cv", default="cv.txt", help="path to CV text")
    parser.add_argument(
        "--output", default="jobs.json", help="path for generated job results"
    )
    args = parser.parse_args(argv)
    main(config_path=args.config, cv_path=args.cv, output_path=args.output)
