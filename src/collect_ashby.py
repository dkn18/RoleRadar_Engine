from datetime import datetime, timezone

import requests


ASHBY_BASE_URL = (
    "https://api.ashbyhq.com/"
    "posting-api/job-board/"
)


def ashby_jobs(job_boards):
    """Collect currently published jobs from public Ashby job boards."""

    jobs = []

    session = requests.Session()

    session.headers.update({
        "User-Agent": "RoleRadar_Engine/1.0"
    })

    for board in job_boards:

        url = f"{ASHBY_BASE_URL}{board}"

        print(
            f"[Ashby] Collecting from {board}..."
        )

        try:

            response = session.get(
                url,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as error:

            print(
                f"[Ashby] Failed for {board}: "
                f"{error}"
            )

            continue

        except ValueError as error:

            print(
                f"[Ashby] Invalid JSON for {board}: "
                f"{error}"
            )

            continue

        company_jobs = data.get(
            "jobs",
            []
        )

        print(
            f"[Ashby] {board}: "
            f"{len(company_jobs)} jobs found"
        )

        for item in company_jobs:

            if not item.get("isListed", True):
                continue

            title = item.get(
                "title",
                ""
            )

            location = item.get(
                "location",
                ""
            )

            secondary_locations = []

            for secondary in (
                item.get(
                    "secondaryLocations"
                )
                or []
            ):

                secondary_location = (
                    secondary.get(
                        "location",
                        ""
                    )
                )

                if secondary_location:
                    secondary_locations.append(
                        secondary_location
                    )

            all_locations = [
                location
            ] + secondary_locations

            location_text = " | ".join(
                dict.fromkeys(
                    loc.strip()
                    for loc in all_locations
                    if loc and loc.strip()
                )
            )

            description = (
                item.get(
                    "descriptionPlain",
                    ""
                )
                or ""
            )

            published_at = item.get(
                "publishedAt",
                ""
            )

            posted_date = ""

            if published_at:

                try:

                    parsed_date = (
                        datetime.fromisoformat(
                            published_at.replace(
                                "Z",
                                "+00:00"
                            )
                        )
                    )

                    posted_date = (
                        parsed_date
                        .astimezone(
                            timezone.utc
                        )
                        .isoformat()
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    posted_date = (
                        published_at
                    )

            job_url = (
                item.get(
                    "jobUrl"
                )
                or item.get(
                    "applyUrl",
                    ""
                )
            )

            jobs.append({

                "source": "Ashby",

                "source_job_id": (
                    job_url
                    or f"{board}:{title}"
                ),

                "title": title,

                "company": board,

                "location": location_text,

                "description": description,

                "url": job_url,

                "posted_date": posted_date
            })

    return jobs
