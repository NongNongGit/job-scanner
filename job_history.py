import json
import os

HISTORY_FILE = "job_history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def filter_new_jobs(jobs):
    history = load_history()
    new_jobs = []

    for job in jobs:
        job_id = job["link"]  # unique identifier
        if job_id not in history:
            history[job_id] = job
            new_jobs.append(job)

    save_history(history)
    return new_jobs
