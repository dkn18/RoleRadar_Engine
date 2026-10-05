import sqlite3
from datetime import datetime


def create_database(db_path):

    connection = sqlite3.connect(
        db_path
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (

            id TEXT,

            title TEXT,

            company TEXT,

            location TEXT,

            description TEXT,

            url TEXT,

            posted_date TEXT,

            source TEXT,

            fingerprint TEXT UNIQUE,

            relevance REAL,

            hiring_confidence REAL,

            red_flags REAL,

            first_seen TEXT,

            last_seen TEXT

        )
    """)

    connection.commit()

    return connection


def save_jobs(connection, jobs):

    cursor = connection.cursor()

    now = datetime.now().isoformat()

    for job in jobs:

        cursor.execute("""
            INSERT INTO jobs (

                id,
                title,
                company,
                location,
                description,
                url,
                posted_date,
                source,
                fingerprint,
                relevance,
                hiring_confidence,
                red_flags,
                first_seen,
                last_seen

            )

            VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?
            )

            ON CONFLICT(fingerprint)
            DO UPDATE SET

                relevance =
                    excluded.relevance,

                hiring_confidence =
                    excluded.hiring_confidence,

                red_flags =
                    excluded.red_flags,

                last_seen =
                    excluded.last_seen
        """, (

            job["id"],
            job["title"],
            job["company"],
            job["location"],
            job["description"],
            job["url"],
            job["posted_date"],
            job["source"],
            job["fingerprint"],
            job["relevance"],
            job["hiring_confidence"],
            job["red_flags"],
            now,
            now
        ))

    connection.commit()
