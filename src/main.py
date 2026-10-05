import os
import html
import yaml
import pandas as pd

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

        return yaml.safe_load(
            file
        )


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
                <a href="{html.escape(
                    job["url"]
                )}">
                    View Job
                </a>
            </td>

        </tr>
        """

    report = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>
            RoleRadar Engine
        </title>

        <style>

            body {{
                font-family: Arial;
                margin: 30px;
            }}

            table {{
                border-collapse:
                    collapse;
                width: 100%;
            }}

            th, td {{
                border:
                    1px solid #ddd;
                padding: 8px;
            }}

            th {{
                background:
                    #f2f2f2;
            }}

        </style>

    </head>

    <body>

        <h1>
            RoleRadar Engine
        </h1>

        <p>
            Live jobs analyzed:
            {len(jobs)}
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

        <p>
            Job data retrieved from
            public job-board APIs.
        </p>

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

    print(
        "Starting RoleRadar Engine..."
    )

    config = load_config()

    # -----------------------
    # Collect
    # -----------------------

    print(
        "Collecting live jobs..."
    )

    jobs = collect_jobs(
        config
    )

    print(
        f"Jobs collected: {len(jobs)}"
    )

    if not jobs:

        print(
            "No jobs collected."
        )

        print(
            "Add Greenhouse or Lever "
            "companies in config.yaml."
        )

        return

    # -----------------------
    # Process
    # -----------------------

    print(
        "Processing jobs..."
    )

    jobs = process_jobs(
        jobs,
        config
    )

    print(
        f"Jobs after filtering: "
        f"{len(jobs)}"
    )

    # -----------------------
    # Score
    # -----------------------

    print(
        "Scoring jobs..."
    )

    jobs = score_jobs(
        jobs
    )

    # -----------------------
    # Directories
    # -----------------------

    os.makedirs(
        "data",
        exist_ok=True
    )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    # -----------------------
    # Database
    # -----------------------

    print(
        "Saving jobs..."
    )

    connection = create_database(
        config["database"]["path"]
    )

    save_jobs(
        connection,
        jobs
    )

    connection.close()

    # -----------------------
    # CSV
    # -----------------------

    dataframe = pd.DataFrame(
        jobs
    )

    dataframe.to_csv(
        config["reports"]["csv"],
        index=False
    )

    # -----------------------
    # HTML
    # -----------------------

    create_html(
        jobs,
        config["reports"]["html"]
    )

    print()

    print(
        "RoleRadar Engine completed."
    )

    print(
        "CSV:",
        config["reports"]["csv"]
    )

    print(
        "HTML:",
        config["reports"]["html"]
    )

    print(
        "Database:",
        config["database"]["path"]
    )


if __name__ == "__main__":
    main()
