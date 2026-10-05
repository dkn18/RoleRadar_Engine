import requests
from datetime import datetime, timezone


def clean_html(text):
    """Remove basic HTML tags from job descriptions."""

    if not text:
        return ""

    import re

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def greenhouse_jobs(boards):
    """Get live jobs from Greenhouse public job boards."""

    jobs = []

    for board in boards:

        url = (
            "https://boards-api.greenhouse.io/"
            f"v1/boards/{board}/jobs"
        )

        params = {
            "content": "true"
        }

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        for job in data.get("jobs", []):

            location = (
                job.get("location") or {}
            ).get("name", "")

            jobs.append({

                "id": str(
                    job.get("id", "")
                ),

                "title": job.get(
                    "title",
                    ""
                ),

                "company": board,

                "location": location,

                "description": clean_html(
                    job.get(
                        "content",
                        ""
                    )
                ),

                "url": job.get(
                    "absolute_url",
                    ""
                ),

                "posted_date": job.get(
                    "updated_at",
                    ""
                ),

                "source": "Greenhouse"

            })

    return jobs


def lever_jobs(companies):
    """Get live jobs from Lever public postings."""

    jobs = []

    for company in companies:

        url = (
            f"https://api.lever.co/v0/postings/"
            f"{company}"
        )

        params = {
            "mode": "json"
        }

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        for job in data:

            categories = (
                job.get("categories") or {}
            )

            description = (
                job.get("descriptionPlain")
                or clean_html(
                    job.get(
                        "description",
                        ""
                    )
                )
            )

            # Lever timestamps are milliseconds.
            created = job.get("createdAt")

            posted_date = ""

            if created:

                posted_date = (
                    datetime.fromtimestamp(
                        created / 1000,
                        tz=timezone.utc
                    ).isoformat()
                )

            jobs.append({

                "id": str(
                    job.get("id", "")
                ),

                "title": job.get(
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
                    job.get("hostedUrl")
                    or job.get(
                        "applyUrl",
                        ""
                    )
                ),

                "posted_date": posted_date,

                "source": "Lever"

            })

    return jobs


def collect_jobs(config):

    jobs = []

    greenhouse = (
        config["sources"]
        ["greenhouse"]
        .get("boards", [])
    )

    lever = (
        config["sources"]
        ["lever"]
        .get("companies", [])
    )

    if greenhouse:

        jobs.extend(
            greenhouse_jobs(
                greenhouse
            )
        )

    if lever:

        jobs.extend(
            lever_jobs(
                lever
            )
        )

    return jobs
