# Job Scanner

A Python-based job scanning and scoring utility that searches for jobs across multiple sources, filters them against your CV and target profiles, and emails the best matches.

Installable Python package with a `job-scanner` command. Configuration, CVs,
profiles, and generated results remain external to the package.

## What it does

- Pulls job listings from LinkedIn and Adzuna
- Loads profile-specific search settings from `profiles/*.json`
- Applies scoring based on your CV keywords, company fit, and salary fit
- Deduplicates jobs by URL
- Saves results to `jobs.json`
- Sends an email summary of the highest-scoring positions

## Requirements

Python 3.10 or newer is required.

Install from a source checkout:

```bash
python -m pip install .
```

For development, install the repository's dependencies:

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
```

## Configuration

The package does not ship configuration, CV, profile, or result data. Keep your
own `config.json`, CV text file, and profile files outside the installed package.
The command defaults to `config.json`, `cv.txt`, and `jobs.json` in the current
working directory, which preserves the existing repository workflow. Override
these paths when running elsewhere:

```bash
job-scanner --config /path/to/config.json --cv /path/to/cv.txt --output /path/to/jobs.json
job-scanner --help
```

The legacy `python main.py` invocation remains supported from a checkout and
accepts the same options.

### 1. Environment variables
Set the required API credentials in environment variables or in a `.env` file
in the current working directory:

```env
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
RAPIDAPI_KEY=your_rapidapi_key
SENDGRID_API_KEY=your_sendgrid_api_key
```

Keep `.env` out of version control if it contains secrets.

### 2. App settings
Create a `config.json` file to match your job search needs:

- `profiles` — map profile names to profile filenames (bare filenames are looked
  up in a `profiles/` directory next to the config) or to paths relative to the
  config file
- `global_keywords` — roles/keywords to search for
- `retry` — retry settings for fetch calls
- `email` — From/to email addresses and subjects
- `scoring` — weightings used to rank jobs

### 3. Profiles
Each profile file contains targeting details such as:

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

## Running from a checkout

```bash
python main.py
```

Options can also be passed to the checkout entry point:

```bash
python main.py --config /path/to/config.json --cv /path/to/cv.txt --output /path/to/jobs.json
```

This will:

1. load all configured profiles
2. collect jobs from LinkedIn and Adzuna
3. score and deduplicate matches
4. write results to the selected output path (default: `jobs.json`)
5. send a daily email summary

## Pre-push validation

Install the repository's Git pre-push hook so every `git push` runs the local
unit tests and coverage check, then validates that source and wheel packages
can be built:

```bash
git config --local core.hooksPath .githooks
```

Install development dependencies, including the `build` package, in the
environment used by the hook:

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
```

The hook uses `labenv`, `.venv`, or `venv` when available, then falls back to
Python on `PATH`. It blocks the push if Python, pytest, or `build` is
unavailable; if tests fail; if total coverage is below 80%; or if the package
build fails. Test coverage data, build inputs, and package artifacts are kept
in a temporary directory and removed after the check; existing `build/` and
`dist/` contents are not used or changed. GitHub Actions applies the same 80%
coverage minimum. The hook builds from a temporary copy of the package sources
so generated metadata cannot affect the checkout. If you build manually, first
create a disposable source copy and run the build from that copy; do not run
`python -m build` from the working checkout, because it can write generated
intermediates into its existing `build/` directory. Keep the build output
directory separate from the source copy, and remove both temporary directories
when finished.

## Notes

- The scoring logic is intentionally tuned to your CV and job preferences.
- Adjust the weights in your config if you want to prioritise salary, company, or CV match more heavily.
- Keep your CV text updated with your latest resume content.
- No license is selected by this packaging change; licensing remains a release decision.
