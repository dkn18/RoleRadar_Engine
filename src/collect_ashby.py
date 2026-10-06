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
                params={
                    "includeCompensation": "true"
                },
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

            # Ignore jobs that are not meant
            # to appear on the public board.
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

            # --------------------------------
            # Secondary locations
            # --------------------------------

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

            # --------------------------------
            # Address
            # --------------------------------

            address = (
                item.get("address")
                or {}
            )

            postal_address = (
                address.get(
                    "postalAddress"
                )
                or {}
            )

            city = postal_address.get(
                "addressLocality",
                ""
            )

            region = postal_address.get(
                "addressRegion",
                ""
            )

            country = postal_address.get(
                "addressCountry",
                ""
            )

            # --------------------------------
            # Job metadata
            # --------------------------------

            department = item.get(
                "department",
                ""
            )

            team = item.get(
                "team",
                ""
            )

            is_remote = item.get(
                "isRemote",
                False
            )

            workplace_type = item.get(
                "workplaceType",
                ""
            )

            employment_type = item.get(
                "employmentType",
                ""
            )

            # --------------------------------
            # Description
            # --------------------------------

            description = (
                item.get(
                    "descriptionPlain",
                    ""
                )
                or ""
            )

            # --------------------------------
            # Published date
            # --------------------------------

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

            # --------------------------------
            # Compensation
            # --------------------------------

            compensation = (
                item.get(
                    "compensation"
                )
                or {}
            )

            compensation_summary = (
                compensation.get(
                    "scrapeableCompensationSalarySummary",
                    ""
                )
                or compensation.get(
                    "compensationTierSummary",
                    ""
                )
            )

            # --------------------------------
            # URLs
            # --------------------------------

            job_url = (
                item.get(
                    "jobUrl"
                )
                or ""
            )

            apply_url = (
                item.get(
                    "applyUrl"
                )
                or job_url
            )

            # --------------------------------
            # Store normalized job
            # --------------------------------

            jobs.append({

                "source": "Ashby",

                "source_job_id": (
                    item.get("id")
                    or job_url
                    or f"{board}:{title}"
                ),

                "title": title,

                "company": board,

                "location": location_text,

                "city": city,

                "region": region,

                "country": country,

                "department": department,

                "team": team,

                "is_remote": is_remote,

                "workplace_type": workplace_type,

                "employment_type": employment_type,

                "description": description,

                "compensation": (
                    compensation_summary
                ),

                "url": job_url,

                "apply_url": apply_url,

                "posted_date": posted_date
            })

    return jobs
