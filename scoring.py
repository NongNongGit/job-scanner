def score_cv_keywords(job, cv_text, profile_config):
    keywords = profile_config["linkedin"]["keywords"]  # global keywords injected
    text = cv_text.lower()
    score = 0

    for kw in keywords:
        if kw.lower() in text:
            score += 10

    return min(score, 100)


def score_company(job):
    # Neutral baseline (no blacklist)
    return 50


def score_salary(job, profile_config):
    salary = job.get("salary", 0)
    min_salary = profile_config["filters"]["min_salary"]

    if salary <= 0:
        return 50
    if salary < min_salary:
        return 30
    if salary >= min_salary * 1.5:
        return 90
    return 70


def score_job(job, cv_text, base_config, profile_config):
    s_cfg = base_config["scoring"]

    cv_score = score_cv_keywords(job, cv_text, profile_config)
    company_score = score_company(job)
    salary_score = score_salary(job, profile_config)

    total = (
        cv_score * s_cfg["cv_keywords_weight"]
        + company_score * s_cfg["company_score_weight"]
        + salary_score * s_cfg["salary_score_weight"]
    )

    return round(total, 2)
