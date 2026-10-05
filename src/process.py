import hashlib
import re
from datetime import datetime


def clean_text(text):

    if not text:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(text)
    ).strip()


def contains_word(text, word):

    if not text or not word:
        return False

    pattern = (
        r"(?<!\w)"
        + re.escape(word.lower())
        + r"(?!\w)"
    )

    return re.search(
        pattern,
        text.lower()
    ) is not None


def days_old(date_string):

    if not date_string:
        return None

    try:

        posted = datetime.fromisoformat(
            date_string.replace(
                "Z",
                "+00:00"
            )
        )

        today = datetime.now(
            posted.tzinfo
        )

        return max(
            0,
            (today - posted).days
        )

    except ValueError:

        try:

            posted = datetime.strptime(
                date_string[:10],
                "%Y-%m-%d"
            )

            return (
                datetime.today()
                - posted
            ).days

        except ValueError:

            return None


def create_fingerprint(job):

    text = "|".join([
        job["company"].lower(),
        job["title"].lower(),
        job["location"].lower()
    ])

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def process_jobs(jobs, config):

    processed = []

    search = config["search"]

    roles = search["roles"]
    locations = search["locations"]

    required_skills = (
        search["required_skills"]
    )

    preferred_skills = (
        search["preferred_skills"]
    )

    exclude_words = (
        search["exclude_words"]
    )

    max_days_old = (
        search["max_days_old"]
    )

    for job in jobs:

        for field in [
            "title",
            "company",
            "location",
            "description",
            "url"
        ]:

            job[field] = clean_text(
                job[field]
            )

        # --------------------
        # Role
        # --------------------

        role_match = any(
            contains_word(
                job["title"],
                role
            )
            for role in roles
        )

        if not role_match:
            continue

        # --------------------
        # Location
        # --------------------

        location_match = any(
            location.lower()
            in job["location"].lower()

            for location in locations
        )

        if not location_match:
            continue

        # --------------------
        # Exclusions
        # --------------------

        full_text = (
            job["title"]
            + " "
            + job["description"]
        )

        excluded = any(
            contains_word(
                full_text,
                word
            )
            for word in exclude_words
        )

        if excluded:
            continue

        # --------------------
        # Required skills
        # --------------------

        matched_required = [
            skill

            for skill in required_skills

            if contains_word(
                full_text,
                skill
            )
        ]

        if len(matched_required) < 2:
            continue

        # --------------------
        # Preferred skills
        # --------------------

        matched_preferred = [
            skill

            for skill in preferred_skills

            if contains_word(
                full_text,
                skill
            )
        ]

        # --------------------
        # Freshness
        # --------------------

        age = days_old(
            job["posted_date"]
        )

        if (
            age is not None
            and age > max_days_old
        ):
            continue

        job["required_skills"] = (
            matched_required
        )

        job["preferred_skills"] = (
            matched_preferred
        )

        job["age_days"] = age

        job["fingerprint"] = (
            create_fingerprint(job)
        )

        processed.append(job)

    return remove_duplicates(
        processed
    )


def remove_duplicates(jobs):

    unique = {}

    for job in jobs:

        fingerprint = (
            job["fingerprint"]
        )

        if fingerprint not in unique:

            job["duplicate_count"] = 0

            unique[fingerprint] = job

        else:

            unique[
                fingerprint
            ]["duplicate_count"] += 1

    return list(
        unique.values()
    )
