# RoleRadar_Engine

A configurable job discovery, data-quality and intelligence pipeline.

```text
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
│   ├── collect_greenhouse.py
│   ├── collect_lever.py
│   ├── collect_ashby.py
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
```

# RoleRadar Engine

RoleRadar Engine is a Python-based job intelligence pipeline that collects live job postings from public **Greenhouse, Lever and Ashby job boards** and prioritizes them based on configurable job-search criteria.

The goal is not just to collect jobs, but to identify which opportunities are most relevant, remove noisy or duplicate listings, and highlight jobs that may require additional verification.

## Pipeline

```text
Greenhouse ──┐
             │
Lever ───────┤
             │
Ashby ───────┤
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
* Live job collection from Ashby public job boards
* Configurable role filtering
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
* SQLite schema migration for new job metadata
* CSV report
* HTML report
* Direct application links
* Unit tests

## Job Data

RoleRadar normalizes job information from different sources into a common structure.

Depending on the source, the pipeline can capture:

* Job title
* Company
* Location
* City
* Region
* Country
* Department
* Team
* Remote status
* Workplace type
* Employment type
* Description
* Compensation
* Job URL
* Application URL
* Posted date
* Required skills
* Preferred skills

This allows jobs from different public job-board systems to be processed consistently.

## Technology

* Python
* REST APIs
* SQLite
* PyYAML
* Pytest
* HTML / CSV reporting

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

Add the public job-board sources you want to monitor.

For example:

```yaml
sources:

  greenhouse:
    boards:
      - companyname

  lever:
    companies:
      - anothercompany

  ashby:
    job_boards:
      - datasnipper
```

Greenhouse and Lever use public job-board endpoints.

Ashby uses its public job-posting interface and does not require an API key for public job boards.

## Configure Job Search Criteria

RoleRadar uses configurable search criteria for the type of jobs it should keep.

Example:

```yaml
search:

  roles:
    - Data Engineer
    - Senior Data Engineer
    - Data Platform Engineer
    - Data Quality Engineer
    - Data Integration Engineer
    - Azure Data Engineer
    - Big Data Engineer
    - Analytics Engineer

  locations:
    - Netherlands
    - Amsterdam
    - Utrecht
    - Rotterdam
    - Eindhoven
    - The Hague
    - Remote
    - Europe

  required_skills:
    - Python
    - SQL

  preferred_skills:
    - Azure
    - Azure Data Factory
    - ADF
    - Databricks
    - Spark
    - PySpark
    - Synapse
    - ADLS
    - ETL
    - Data Lake
    - REST API
    - Terraform
    - Git

  exclude_words:
    - internship
    - intern
    - unpaid

  max_days_old: 30
```

The configuration can be changed without modifying the pipeline code.

## Run

From the project root:

```bash
python -m src.main
```

The pipeline will:

1. Retrieve live jobs
2. Normalize and clean job data
3. Filter by role
4. Filter by location
5. Match required and preferred skills
6. Filter older listings
7. Remove duplicates
8. Calculate scores
9. Store jobs in SQLite
10. Generate CSV and HTML reports

## Output

```text
data/
└── roleradar.db

reports/
├── daily_jobs.csv
└── daily_jobs.html
```

The HTML report includes information such as:

* Role
* Company
* Location
* Workplace type
* Employment type
* Department
* Compensation
* Relevance
* Hiring confidence
* Red flags
* Skills
* Warnings
* Recommended action
* Application link

## Database

RoleRadar uses SQLite to store processed job information.

The database tracks:

* Job source
* Source job ID
* Job details
* Posting date
* Fingerprint
* Relevance
* Hiring confidence
* Red flags
* First seen
* Last seen
* Number of times seen
* Location metadata
* Department and team
* Remote/workplace information
* Employment type
* Compensation
* Application URL

The database initialization includes schema migration support so new fields can be added without manually recreating the existing database.

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

## Deduplication

RoleRadar creates a fingerprint using job attributes such as:

```text
Company + Job Title + Location
```

This helps identify duplicate listings across repeated collections and different sources.

Repeated sightings are tracked using `first_seen`, `last_seen` and `times_seen`.

## Data Sources

RoleRadar Engine currently supports public job-posting interfaces from:

* Greenhouse
* Lever
* Ashby

Greenhouse Job Board API documentation:

https://developers.greenhouse.io/job-board.html

Lever Postings API documentation:

https://hire.lever.co/developer/documentation

Ashby Public Job Posting API documentation:

https://developers.ashbyhq.com/docs/public-job-posting-api

## Testing

Run:

```bash
pytest
```

## Future Improvements

* More public ATS sources
* More company job boards
* Automated job-source discovery
* Broader Data Engineering role detection
* Improved remote-job detection
* Better repost detection
* Historical job tracking
* Company-level hiring signals
* Web-based job discovery
* Email notifications
* Dashboard
* Cloud deployment

## Disclaimer

RoleRadar Engine provides heuristic scores based on available job-posting information. Scores should not be interpreted as guarantees about employers, hiring activity, or job availability.
