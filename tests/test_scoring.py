from scoring import score_job


def test_score_job():
    base = {
        "scoring": {
            "cv_keywords_weight": 0.6,
            "company_score_weight": 0.2,
            "salary_score_weight": 0.2,
            "min_score_to_email": 50,
        }
    }

    profile = {
        "filters": {"min_salary": 80000},
        "linkedin": {"keywords": ["Software Engineer", "Backend Developer"]},
    }

    cv_text = "I worked as a Software Engineer building backend systems."

    job = {
        "title": "Software Engineer",
        "company": "Microsoft",
        "location": "Auckland",
        "salary": 120000,
    }

    score = score_job(job, cv_text, base, profile)
    assert score >= 30


def test_score_salary_for_missing_low_and_mid_range_salaries():
    from scoring import score_salary

    profile = {"filters": {"min_salary": 80000}}

    assert score_salary({}, profile) == 50
    assert score_salary({"salary": 60000}, profile) == 30
    assert score_salary({"salary": 100000}, profile) == 70
