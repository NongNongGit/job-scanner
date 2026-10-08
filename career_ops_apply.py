import subprocess
import json


def auto_apply(job):
    """
    Uses Career-Ops agent to auto-apply to a job.
    Requires career-ops CLI installed locally.
    """

    cmd = [
        "career-ops",
        "apply",
        "--job-title",
        job["title"],
        "--company",
        job["company"],
        "--location",
        job["location"],
        "--url",
        job["link"],
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "job": job,
            "status": "success" if result.returncode == 0 else "failed",
            "output": result.stdout,
        }
    except Exception as e:
        return {"job": job, "status": "error", "output": str(e)}
