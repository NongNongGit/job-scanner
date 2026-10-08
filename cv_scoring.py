import re

# Load CV text from a file (you can paste your CV into cv.txt)
CV_FILE = "cv.txt"


def load_cv_keywords():
    with open(CV_FILE, "r", encoding="utf-8") as f:
        text = f.read().lower()

    # Extract keywords (simple version)
    keywords = re.findall(r"[a-zA-Z0-9\+#\.]+", text)
    return set(keywords)


CV_KEYWORDS = load_cv_keywords()


def score_job(job_description):
    """
    Score job 1–5 based on keyword overlap with CV.
    """
    desc = job_description.lower()
    words = re.findall(r"[a-zA-Z0-9\+#\.]+", desc)

    match_count = sum(1 for w in words if w in CV_KEYWORDS)

    if match_count > 40:
        return 5
    elif match_count > 25:
        return 4
    elif match_count > 15:
        return 3
    elif match_count > 5:
        return 2
    else:
        return 1
