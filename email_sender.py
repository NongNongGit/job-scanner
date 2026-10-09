import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from report import build_html


def send_email(jobs, base_config):
    email_cfg = base_config["email"]
    html = build_html(jobs)

    message = Mail(
        from_email=email_cfg["from"],
        to_emails=email_cfg["to"],
        subject=email_cfg["subject"],
        html_content=html,
    )

    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    sg.send(message)


def send_summary(summary_text, base_config):
    email_cfg = base_config["email"]

    message = Mail(
        from_email=email_cfg["from"],
        to_emails=email_cfg["to"],
        subject=email_cfg["summary_subject"],
        html_content=f"<pre>{summary_text}</pre>",
    )

    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    sg.send(message)
