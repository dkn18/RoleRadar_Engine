import sqlite3
from datetime import datetime


def create_database(db_path):

    connection = sqlite3.connect(
        db_path
    )

    cursor = connection.cursor()

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
                    description = ?

                WHERE fingerprint = ?
                """,
                (
                    job["relevance"],
                    job[
                        "hiring_confidence"
                    ],
                    job["red_flags"],
                    now,
                    times_seen,
                    job["url"],
                    job["description"],
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
                    times_seen

                )

                VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?
                )
                """,
                (
                    job["source"],
                    job[
                        "source_job_id"
                    ],
                    job["title"],
                    job["company"],
                    job["location"],
                    job["description"],
                    job["url"],
                    job["posted_date"],
                    job["fingerprint"],
                    job["relevance"],
                    job[
                        "hiring_confidence"
                    ],
                    job["red_flags"],
                    now,
                    now,
                    1
                )
            )

    connection.commit()
