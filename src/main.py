import html
import os

import pandas as pd
import yaml

from collect import collect_jobs
from process import process_jobs
from score import score_jobs
from database import (
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
            job["required_skills"]
            +
            job["preferred_skills"]
        )

        warnings = ", ".join(
            job["warnings"]
        )

        rows += f"""
        <tr>

            <td>
                {html.escape(
                    job["action"]
                )}
            </td>

            <td>
                {html.escape(
                    job["title"]
                )}
            </td>

            <td>
                {html.escape(
                    job["company"]
                )}
            </td>

            <td>
                {html.escape(
                    job["location"]
                )}
            </td>

            <td>
                {job["relevance"]}
            </td>

            <td>
                {job["hiring_confidence"]}
            </td>

            <td>
                {job["red_flags"]}
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
                        job["url"],
                        quote=True
                    )}"
                    target="_blank"
                >
                    View Job
                </a>
            </td>

        </tr>
        """

    report = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

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
}}

th {{
    background: #f2f2f2;
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
    <th>Relevance</th>
    <th>Hiring Confidence</th>
    <th>Red Flags</th>
    <th>Skills</th>
    <th>Warnings</th>
    <th>Job</th>
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
