import re
from datetime import datetime, timezone

import requests


def clean_html(text):
    """Convert basic HTML content into readable plain text."""

    if not text:
        return ""

    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def greenhouse_jobs(boards):
    """Collect live jobs from public Greenhouse job boards."""

    jobs = []

    session = requests.Session()

    for board in boards:

        url = (
            f"https://boards-api.greenhouse.io/"
            f"v1/boards/{board}/jobs"
        )

        try:

            response = session.get(
                url,
                params={"content": "true"},
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as error:

            print(
                f"[Greenhouse] Failed for {board}: "
                f"{error}"
            )

            continue

        for item in data.get("jobs", []):

            location_data = (
                item.get("location") or {}
            )

            location = location_data.get(
                "name",
                ""
            )

            jobs.append({

                "source": "Greenhouse",

                "source_job_id": str(
                    item.get("id", "")
                ),

                "title": item.get(
                    "title",
                    ""
                ),

                "company": board,

                "location": location,

                "description": clean_html(
                    item.get(
                        "content",
                        ""
                    )
                ),

                "url": item.get(
                    "absolute_url",
                    ""
                ),

                "posted_date": item.get(
                    "updated_at",
                    ""
                )
            })

    return jobs


def lever_jobs(companies):
    """Collect live jobs from public Lever postings."""

    jobs = []

    session = requests.Session()

    for company in companies:

        url = (
            f"https://api.lever.co/v0/postings/"
            f"{company}"
        )

        try:

            response = session.get(
                url,
                params={"mode": "json"},
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as error:

            print(
                f"[Lever] Failed for {company}: "
                f"{error}"
            )

            continue

        for item in data:

            categories = (
                item.get("categories") or {}
            )

            description = (
                item.get("descriptionPlain")
                or clean_html(
                    item.get(
                        "description",
                        ""
                    )
                )
            )

            created_at = item.get(
                "createdAt"
            )

            posted_date = ""

            if created_at:

                try:

                    posted_date = (
                        datetime.fromtimestamp(
                            created_at / 1000,
                            tz=timezone.utc
                        ).isoformat()
                    )

                except (
                    TypeError,
                    ValueError,
                    OSError
                ):

                    posted_date = ""

            jobs.append({

                "source": "Lever",

                "source_job_id": str(
                    item.get("id", "")
                ),

                "title": item.get(
                    "text",
                    ""
                ),

                "company": company,

                "location": categories.get(
                    "location",
                    ""
                ),

                "description": description,

                "url": (
                    item.get("hostedUrl")
                    or item.get(
                        "applyUrl",
                        ""
                    )
                ),

                "posted_date": posted_date
            })

    return jobs


def collect_jobs(config):

    jobs = []

    greenhouse_boards = (
        config["sources"]
        ["greenhouse"]
        .get("boards", [])
    )

    lever_companies = (
        config["sources"]
        ["lever"]
        .get("companies", [])
    )

    if greenhouse_boards:

        print(
            "Collecting from Greenhouse..."
        )

        jobs.extend(
            greenhouse_jobs(
                greenhouse_boards
            )
        )

    if lever_companies:

        print(
            "Collecting from Lever..."
        )

        jobs.extend(
            lever_jobs(
                lever_companies
            )
        )

    return jobs
