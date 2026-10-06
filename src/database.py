import sqlite3
from datetime import datetime


def create_database(db_path):

    connection = sqlite3.connect(
        db_path
    )

    cursor = connection.cursor()

    # ---------------------------------
    # Original schema
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (

            source TEXT NOT NULL,

            source_job_id TEXT,

            title TEXT,

            company TEXT,

            location TEXT,

            description TEXT,

            url TEXT,

            posted_date TEXT,

            fingerprint TEXT UNIQUE,

            relevance INTEGER,

            hiring_confidence INTEGER,

            red_flags INTEGER,

            first_seen TEXT,

            last_seen TEXT,

            times_seen INTEGER DEFAULT 1

        )
    """)

    # ---------------------------------
    # Add extended job fields
    # ---------------------------------

    existing_columns = {
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(jobs)"
        ).fetchall()
    }

    new_columns = {

        "city": "TEXT",

        "region": "TEXT",

        "country": "TEXT",

        "department": "TEXT",

        "team": "TEXT",

        "is_remote": "INTEGER",

        "workplace_type": "TEXT",

        "employment_type": "TEXT",

        "compensation": "TEXT",

        "apply_url": "TEXT"
    }

    for column, data_type in new_columns.items():

        if column not in existing_columns:

            cursor.execute(
                f"""
                ALTER TABLE jobs
                ADD COLUMN {column} {data_type}
                """
            )

    connection.commit()

    return connection


def save_jobs(
    connection,
    jobs
):

    cursor = connection.cursor()

    now = datetime.now().isoformat()

    for job in jobs:

        cursor.execute(
            """
            SELECT
                fingerprint,
                times_seen
            FROM jobs
            WHERE fingerprint = ?
            """,
            (
                job["fingerprint"],
            )
        )

        existing = cursor.fetchone()

        if existing:

            times_seen = (
                existing[1] + 1
            )

            cursor.execute(
                """
                UPDATE jobs

                SET
                    relevance = ?,
                    hiring_confidence = ?,
                    red_flags = ?,
                    last_seen = ?,
                    times_seen = ?,
                    url = ?,
                    apply_url = ?,
                    description = ?,
                    city = ?,
                    region = ?,
                    country = ?,
                    department = ?,
                    team = ?,
                    is_remote = ?,
                    workplace_type = ?,
                    employment_type = ?,
                    compensation = ?

                WHERE fingerprint = ?
                """,
                (
                    job["relevance"],
                    job["hiring_confidence"],
                    job["red_flags"],
                    now,
                    times_seen,

                    job.get(
                        "url",
                        ""
                    ),

                    job.get(
                        "apply_url",
                        job.get("url", "")
                    ),

                    job.get(
                        "description",
                        ""
                    ),

                    job.get(
                        "city",
                        ""
                    ),

                    job.get(
                        "region",
                        ""
                    ),

                    job.get(
                        "country",
                        ""
                    ),

                    job.get(
                        "department",
                        ""
                    ),

                    job.get(
                        "team",
                        ""
                    ),

                    int(
                        bool(
                            job.get(
                                "is_remote",
                                False
                            )
                        )
                    ),

                    job.get(
                        "workplace_type",
                        ""
                    ),

                    job.get(
                        "employment_type",
                        ""
                    ),

                    job.get(
                        "compensation",
                        ""
                    ),

                    job["fingerprint"]
                )
            )

        else:

            cursor.execute(
                """
                INSERT INTO jobs (

                    source,
                    source_job_id,
                    title,
                    company,
                    location,
                    description,
                    url,
                    posted_date,

                    fingerprint,

                    relevance,
                    hiring_confidence,
                    red_flags,

                    first_seen,
                    last_seen,
                    times_seen,

                    city,
                    region,
                    country,
                    department,
                    team,
                    is_remote,
                    workplace_type,
                    employment_type,
                    compensation,
                    apply_url

                )

                VALUES (
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?
                )
                """,
                (
                    job["source"],

                    job.get(
                        "source_job_id",
                        ""
                    ),

                    job.get(
                        "title",
                        ""
                    ),

                    job.get(
                        "company",
                        ""
                    ),

                    job.get(
                        "location",
                        ""
                    ),

                    job.get(
                        "description",
                        ""
                    ),

                    job.get(
                        "url",
                        ""
                    ),

                    job.get(
                        "posted_date",
                        ""
                    ),

                    job["fingerprint"],

                    job.get(
                        "relevance",
                        0
                    ),

                    job.get(
                        "hiring_confidence",
                        0
                    ),

                    job.get(
                        "red_flags",
                        0
                    ),

                    now,
                    now,
                    1,

                    job.get(
                        "city",
                        ""
                    ),

                    job.get(
                        "region",
                        ""
                    ),

                    job.get(
                        "country",
                        ""
                    ),

                    job.get(
                        "department",
                        ""
                    ),

                    job.get(
                        "team",
                        ""
                    ),

                    int(
                        bool(
                            job.get(
                                "is_remote",
                                False
                            )
                        )
                    ),

                    job.get(
                        "workplace_type",
                        ""
                    ),

                    job.get(
                        "employment_type",
                        ""
                    ),

                    job.get(
                        "compensation",
                        ""
                    ),

                    job.get(
                        "apply_url",
                        job.get("url", "")
                    )
                )
            )

    connection.commit()
