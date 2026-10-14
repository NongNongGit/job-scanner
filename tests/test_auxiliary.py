import json
from types import SimpleNamespace

import career_ops_apply
import email_sender
import job_history
import report


def test_filter_new_jobs_persists_only_first_occurrence(tmp_path, monkeypatch):
    history_file = tmp_path / "job_history.json"
    monkeypatch.setattr(job_history, "HISTORY_FILE", str(history_file))

    first_job = {"link": "https://example.com/job/1", "title": "Engineer"}
    duplicate_job = {"link": "https://example.com/job/1", "title": "Duplicate"}
    second_job = {"link": "https://example.com/job/2", "title": "Developer"}

    assert job_history.load_history() == {}
    assert job_history.filter_new_jobs([first_job, duplicate_job, second_job]) == [
        first_job,
        second_job,
    ]
    assert json.loads(history_file.read_text()) == {
        first_job["link"]: first_job,
        second_job["link"]: second_job,
    }
    assert job_history.load_history() == {
        first_job["link"]: first_job,
        second_job["link"]: second_job,
    }


def test_build_html_includes_job_details():
    html = report.build_html(
        [
            {
                "title": "Engineer",
                "company": "Example Co",
                "location": "Auckland",
                "salary": 120000,
                "score": 85,
                "url": "https://example.com/job/1",
            }
        ]
    )

    assert "Engineer" in html
    assert "Example Co" in html
    assert "Auckland" in html
    assert "120000" in html
    assert "85" in html
    assert 'href="https://example.com/job/1"' in html


def test_send_email_and_summary_use_sendgrid(monkeypatch):
    sent_messages = []

    class FakeMail:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeSendGridClient:
        def __init__(self, api_key):
            assert api_key == "test-api-key"

        def send(self, message):
            sent_messages.append(message)

    monkeypatch.setenv("SENDGRID_API_KEY", "test-api-key")
    monkeypatch.setattr(email_sender, "Mail", FakeMail)
    monkeypatch.setattr(email_sender, "SendGridAPIClient", FakeSendGridClient)
    monkeypatch.setattr(email_sender, "build_html", lambda jobs: "<p>jobs</p>")

    config = {
        "email": {
            "from": "sender@example.com",
            "to": "recipient@example.com",
            "subject": "Jobs",
            "summary_subject": "Summary",
        }
    }
    email_sender.send_email([{"title": "Engineer"}], config)
    email_sender.send_summary("1 job", config)

    assert len(sent_messages) == 2
    assert sent_messages[0].kwargs["subject"] == "Jobs"
    assert sent_messages[0].kwargs["html_content"] == "<p>jobs</p>"
    assert sent_messages[1].kwargs["subject"] == "Summary"
    assert sent_messages[1].kwargs["html_content"] == "<pre>1 job</pre>"


def test_auto_apply_reports_process_result_and_error(monkeypatch):
    job = {
        "title": "Engineer",
        "company": "Example Co",
        "location": "Auckland",
        "link": "https://example.com/job/1",
    }
    monkeypatch.setattr(
        career_ops_apply.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="applied"),
    )
    assert career_ops_apply.auto_apply(job) == {
        "job": job,
        "status": "success",
        "output": "applied",
    }

    monkeypatch.setattr(
        career_ops_apply.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout="rejected"),
    )
    assert career_ops_apply.auto_apply(job)["status"] == "failed"

    def raise_process_error(*args, **kwargs):
        raise OSError("career-ops not installed")

    monkeypatch.setattr(career_ops_apply.subprocess, "run", raise_process_error)
    assert career_ops_apply.auto_apply(job) == {
        "job": job,
        "status": "error",
        "output": "career-ops not installed",
    }
