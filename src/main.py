import html
import os

import pandas as pd
import yaml

from src.collect import collect_jobs
from src.process import process_jobs
from src.score import score_jobs
from src.database import (
    create_database,
    save_jobs
)


def load_config():

    with open(
        "config/config.yaml",
        "r",
        encoding="utf-8"
    ) as file:

        return yaml.safe_load(file)


def create_html(
    jobs,
    output_file
):

    rows = ""

    for job in jobs:

        skills = ", ".join(
            job.get("required_skills", [])
            +
            job.get("preferred_skills", [])
        )

        warnings = ", ".join(
            job.get("warnings", [])
        )

        apply_url = (
            job.get("apply_url")
            or job.get("url")
            or ""
        )

        compensation = (
            job.get("compensation")
            or "Not specified"
        )

        workplace_type = (
            job.get("workplace_type")
            or "Not specified"
        )

        employment_type = (
            job.get("employment_type")
            or "Not specified"
        )

        department = (
            job.get("department")
            or ""
        )

        rows += f"""
        <tr>

            <td>
                {html.escape(
                    job.get("action", "")
                )}
            </td>

            <td>
                {html.escape(
                    job.get("title", "")
                )}
            </td>

            <td>
                {html.escape(
                    job.get("company", "")
                )}
            </td>

            <td>
                {html.escape(
                    job.get("location", "")
                )}
            </td>

            <td>
                {html.escape(
                    workplace_type
                )}
            </td>

            <td>
                {html.escape(
                    employment_type
                )}
            </td>

            <td>
                {html.escape(
                    department
                )}
            </td>

            <td>
                {html.escape(
                    compensation
                )}
            </td>

            <td>
                {job.get("relevance", 0)}
            </td>

            <td>
                {job.get(
                    "hiring_confidence",
                    0
                )}
            </td>

            <td>
                {job.get(
                    "red_flags",
                    0
                )}
            </td>

            <td>
                {html.escape(
                    skills
                )}
            </td>

            <td>
                {html.escape(
                    warnings
                )}
            </td>

            <td>
                <a
                    href="{html.escape(
                        apply_url,
                        quote=True
                    )}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Apply
                </a>
            </td>

        </tr>
        """

    report = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,
      initial-scale=1.0">

<title>
RoleRadar Engine
</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 30px;
}}

table {{
    border-collapse: collapse;
    width: 100%;
}}

th, td {{
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
    vertical-align: top;
}}

th {{
    background: #f2f2f2;
    position: sticky;
    top: 0;
}}

tr:hover {{
    background: #f8f8f8;
}}

a {{
    text-decoration: none;
}}

</style>

</head>

<body>

<h1>
RoleRadar Engine
</h1>

<p>
Live jobs analyzed:
<strong>{len(jobs)}</strong>
</p>

<table>

<tr>
    <th>Action</th>
    <th>Role</th>
    <th>Company</th>
    <th>Location</th>
    <th>Workplace</th>
    <th>Employment</th>
    <th>Department</th>
    <th>Compensation</th>
    <th>Relevance</th>
    <th>Hiring Confidence</th>
    <th>Red Flags</th>
    <th>Skills</th>
    <th>Warnings</th>
    <th>Apply</th>
</tr>

{rows}

</table>

</body>

</html>
"""

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report)


def main():

    print()
    print(
        "================================"
    )
    print(
        "       RoleRadar Engine"
    )
    print(
        "================================"
    )
    print()

    config = load_config()

    # -------------------------
    # Collect
    # -------------------------

    print(
        "[1/5] Collecting live jobs..."
    )

    jobs = collect_jobs(
        config
    )

    print(
        f"      Collected: {len(jobs)}"
    )

    if not jobs:

        print()
        print(
            "No jobs were collected."
        )

        print(
            "Check your source configuration."
        )

        return

    # -------------------------
    # Process
    # -------------------------

    print(
        "[2/5] Filtering and cleaning..."
    )

    jobs = process_jobs(
        jobs,
        config
    )

    print(
        f"      Matching jobs: {len(jobs)}"
    )

    if not jobs:

        print()
        print(
            "Jobs were collected, but "
            "none matched your filters."
        )

        print(
            "Try increasing max_days_old "
            "or checking your role/location "
            "filters."
        )

        return

    # -------------------------
    # Score
    # -------------------------

    print(
        "[3/5] Scoring jobs..."
    )

    jobs = score_jobs(
        jobs
    )

    apply_count = sum(
        1
        for job in jobs
        if job["action"] == "APPLY"
    )

    verify_count = sum(
        1
        for job in jobs
        if job["action"] == "VERIFY"
    )

    skip_count = sum(
        1
        for job in jobs
        if job["action"] == "SKIP"
    )

    print(
        f"      APPLY: {apply_count}"
    )

    print(
        f"      VERIFY: {verify_count}"
    )

    print(
        f"      SKIP: {skip_count}"
    )

    # -------------------------
    # Directories
    # -------------------------

    os.makedirs(
        "data",
        exist_ok=True
    )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    # -------------------------
    # Database
    # -------------------------

    print(
        "[4/5] Updating SQLite..."
    )

    connection = create_database(
        config["database"]["path"]
    )

    save_jobs(
        connection,
        jobs
    )

    connection.close()

    # -------------------------
    # Reports
    # -------------------------

    print(
        "[5/5] Creating reports..."
    )

    dataframe = pd.DataFrame(
        jobs
    )

    dataframe.to_csv(
        config["reports"]["csv"],
        index=False
    )

    create_html(
        jobs,
        config["reports"]["html"]
    )

    print()
    print(
        "================================"
    )
    print(
        "        Run completed"
    )
    print(
        "================================"
    )

    print()
    print(
        f"CSV:      "
        f"{config['reports']['csv']}"
    )

    print(
        f"HTML:     "
        f"{config['reports']['html']}"
    )

    print(
        f"Database: "
        f"{config['database']['path']}"
    )

    print()


if __name__ == "__main__":
    main()