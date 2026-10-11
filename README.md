# Job Scanner

A Python-based job scanning and scoring utility that searches for jobs across multiple sources, filters them against your CV and target profiles, and emails the best matches.

## What it does

- Pulls job listings from LinkedIn and Adzuna
- Loads profile-specific search settings from `profiles/*.json`
- Applies scoring based on your CV keywords, company fit, and salary fit
- Deduplicates jobs by URL
- Saves results to `jobs.json`
- Sends an email summary of the highest-scoring positions

## Project structure

- `main.py` — entry point
- `linkedin_scraper.py` — LinkedIn job scraping logic
- `adzuna_scraper.py` — Adzuna API integration
- `filters.py` — custom filtering logic
- `scoring.py` — ranking logic for job matches
- `email_sender.py` — SendGrid email sending
- `config.json` — global scanner settings and email configuration
- `profiles/` — country/role-specific search profiles
- `cv.txt` — your CV text used for scoring
- `jobs.json` — generated job output
- `job_history.py` and `job_history.json` — deduping/history support

## Requirements

Python 3.10+ is recommended.

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Environment variables
Create a `.env` file in the project root with the required API credentials:

```env
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
RAPIDAPI_KEY=your_rapidapi_key
SENDGRID_API_KEY=your_sendgrid_api_key
```

Note: keep this file out of version control if it contains secrets.

### 2. App settings
Edit `config.json` to match your job search needs:

- `profiles` — map profile names to files in `profiles/`
- `global_keywords` — roles/keywords to search for
- `retry` — retry settings for fetch calls
- `email` — From/to email addresses and subjects
- `scoring` — weightings used to rank jobs

### 3. Profiles
Each file under `profiles/` contains targeting details such as:

- country
- location
- job title filters
- salary preferences
- keyword lists for LinkedIn/Adzuna

Example:

```json
{
  "linkedin": {
    "country": "au",
    "location": "Sydney",
    "keywords": []
  },
  "adzuna": {
    "country": "au",
    "location": "Sydney",
    "keywords": []
  }
}
```

## Running the scanner

```bash
python main.py
```

This will:

1. load all configured profiles
2. collect jobs from LinkedIn and Adzuna
3. score and deduplicate matches
4. write results to `jobs.json`
5. send a daily email summary

## Notes

- The scoring logic is intentionally tuned to your CV and job preferences.
- Adjust the weights in `config.json` if you want to prioritise salary, company, or CV match more heavily.
- For best results, keep `cv.txt` updated with your latest resume content.

## License

This project is provided as-is for personal or internal job-search automation.
