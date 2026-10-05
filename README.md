# RoleRadar_Engine
A configurable job discovery, data-quality and intelligence pipeline.

RoleRadar_Engine/
│
├── config/
│   └── config.yaml
│
├── data/
│   └── .gitkeep
│
├── reports/
│   └── .gitkeep
│
├── src/
│   ├── collect.py
│   ├── process.py
│   ├── score.py
│   ├── database.py
│   └── main.py
│
├── tests/
│   └── test_pipeline.py
│
├── .gitignore
├── requirements.txt
└── pyproject.toml

# RoleRadar Engine

RoleRadar Engine is a Python-based job intelligence pipeline that collects live job postings from public Greenhouse and Lever job boards and prioritizes them based on configurable job-search criteria.

The goal is not just to collect jobs, but to identify which opportunities are most relevant and which listings may require additional verification.

## Pipeline

```text
Greenhouse ──┐
             │
Lever ───────┤
             ↓
        Collect Jobs
             ↓
       Clean & Filter
             ↓
        Deduplicate
             ↓
           Score
             ↓
          SQLite
             ↓
      CSV + HTML Report
```

## Features

* Live job collection from Greenhouse public job boards
* Live job collection from Lever public postings
* Role filtering
* Location filtering
* Required skill matching
* Preferred skill matching
* Exclusion rules
* Job freshness filtering
* Duplicate detection
* Relevance scoring
* Hiring-confidence scoring
* Red-flag scoring
* APPLY / VERIFY / SKIP recommendation
* SQLite storage
* CSV report
* HTML report
* Unit tests

## Technology

* Python
* REST APIs
* Pandas
* SQLite
* PyYAML
* Pytest

## Setup

Clone the repository:

```bash
git clone <your-repository-url>
cd RoleRadar_Engine
```

Create a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configure Job Sources

Open:

```text
config/config.yaml
```

Add Greenhouse board tokens and/or Lever company slugs.

For example:

```yaml
sources:

  greenhouse:
    boards:
      - companyname

  lever:
    companies:
      - anothercompany
```

The project does not require API keys for these public job-board endpoints.

## Run

From the project root:

```bash
python src/main.py
```

The pipeline will:

1. Retrieve live jobs
2. Clean job data
3. Filter by role
4. Filter by location
5. Match required and preferred skills
6. Remove duplicates
7. Calculate scores
8. Store jobs in SQLite
9. Generate CSV and HTML reports

## Output

```text
data/
└── roleradar.db

reports/
├── daily_jobs.csv
└── daily_jobs.html
```

## Scoring

### Relevance Score

Measures how closely a job matches the configured:

* Role
* Required skills
* Preferred skills
* Location
* Freshness

### Hiring Confidence

Uses basic observable signals such as:

* Company identified
* Job URL available
* Recent posting
* Description quality

This is an explainable indicator and is not a guarantee that an employer is actively hiring.

### Red Flag Score

Highlights listings that may require additional verification.

Examples include:

* Missing company
* Missing URL
* Short description
* Older posting
* Duplicate listing

### Recommendation

Jobs are classified as:

```text
APPLY
VERIFY
SKIP
```

The recommendation is based on the configured scoring rules and is intended to support job research.

## Data Sources

RoleRadar Engine uses public job-posting interfaces provided by Greenhouse and Lever.

Greenhouse Job Board API documentation:
https://developers.greenhouse.io/job-board.html

Lever Postings API documentation:
https://hire.lever.co/developer/documentation

## Testing

Run:

```bash
pytest
```

## Future Improvements

* More public ATS sources
* Better repost detection
* Historical job tracking
* Company-level signals
* Email notifications
* Dashboard
* Cloud deployment

## Disclaimer

RoleRadar Engine provides heuristic scores based on available job-posting information. Scores should not be interpreted as guarantees about employers, hiring activity, or job availability.
