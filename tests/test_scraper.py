import linkedin_scraper
import adzuna_scraper


def test_normalize_list():
    assert linkedin_scraper.normalize(["A", "B"]) == "A, B"


def test_normalize_none():
    assert linkedin_scraper.normalize(None) == ""


def test_scraper_normalization(monkeypatch):
    def fake_get(url, headers, params):
        class FakeResponse:
            def json(self):
                return {
                    "data": [
                        {
                            "title": ["Software Engineer"],
                            "company": ["Microsoft", "NZ"],
                            "location": ["Auckland"],
                            "salary": 100000,
                            "url": "http://example.com",
                            "description": ["Great job"],
                        }
                    ]
                }

        return FakeResponse()

    monkeypatch.setattr("requests.get", fake_get)

    profile = {
        "linkedin": {
            "keywords": ["Software Engineer"],
            "location": "Auckland",
            "job_types": ["full-time"],
            "max_results": 10,
        }
    }

    jobs = linkedin_scraper.fetch_linkedin_jobs(profile)

    assert len(jobs) == 1
    job = jobs[0]

    assert job["title"] == "Software Engineer"
    assert job["company"] == "Microsoft, NZ"
    assert job["location"] == "Auckland"
    assert job["salary"] == 100000


def test_adzuna_requests_each_sanitized_keyword_and_deduplicates_by_url(monkeypatch):
    requests_made = []

    def fake_get(url, params):
        requests_made.append((url, params.copy()))
        keyword = params["what"]
        results = [
            {
                "title": f"{keyword} role",
                "company": {"display_name": "Example Co"},
                "location": {"display_name": "Auckland"},
                "redirect_url": "https://example.com/shared",
                "description": "Shared job",
            }
        ]
        if keyword == "python":
            results.append(
                {
                    "title": "Distinct role",
                    "company": {"display_name": "Other Co"},
                    "location": {"display_name": "Wellington"},
                    "redirect_url": "https://example.com/distinct",
                    "description": "Another job",
                }
            )

        class FakeResponse:
            def json(self):
                return {"results": results}

        return FakeResponse()

    monkeypatch.setattr(adzuna_scraper.requests, "get", fake_get)

    profile = {
        "adzuna": {
            "country": "nz",
            "keywords": ["C#.", "PY.THON"],
            "location": "Auckland",
        }
    }

    jobs = adzuna_scraper.fetch_adzuna_jobs(profile)

    assert [params["what"] for _, params in requests_made] == ["c", "python"]
    assert all(url.endswith("/nz/search/1") for url, _ in requests_made)
    assert [job["url"] for job in jobs] == [
        "https://example.com/shared",
        "https://example.com/distinct",
    ]
    assert jobs[0]["title"] == "c role"
    assert jobs[1]["source"] == "adzuna"


def test_adzuna_continues_after_keyword_request_failure(monkeypatch, capsys):
    requests_made = []

    def fake_get(url, params):
        keyword = params["what"]
        requests_made.append(keyword)
        if keyword == "broken":
            raise RuntimeError("request failed")

        class FakeResponse:
            def json(self):
                return {
                    "results": [
                        {
                            "title": "Working role",
                            "company": {"display_name": "Example Co"},
                            "location": {"display_name": "Auckland"},
                            "redirect_url": "https://example.com/working",
                            "description": "A working job",
                        }
                    ]
                }

        return FakeResponse()

    monkeypatch.setattr(adzuna_scraper.requests, "get", fake_get)

    profile = {
        "adzuna": {
            "country": "nz",
            "keywords": ["broken", "working"],
            "location": "Auckland",
        }
    }

    jobs = adzuna_scraper.fetch_adzuna_jobs(profile)

    assert requests_made == ["broken", "working"]
    assert [job["url"] for job in jobs] == ["https://example.com/working"]
    assert "Adzuna error: request failed" in capsys.readouterr().out
