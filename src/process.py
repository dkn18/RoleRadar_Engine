import hashlib
import re
from datetime import datetime, timezone


def clean_text(text):

    if not text:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(text)
    ).strip()


def contains_word(text, phrase):

    if not text or not phrase:
        return False

    pattern = (
        r"(?<!\w)"
        + re.escape(
            phrase.lower()
        )
        + r"(?!\w)"
    )

    return (
        re.search(
            pattern,
            text.lower()
        ) is not None
    )


def parse_date(date_string):

    if not date_string:
        return None

    try:

        return datetime.fromisoformat(
            date_string.replace(
                "Z",
                "+00:00"
            )
        )

    except ValueError:

        try:

            return datetime.strptime(
                date_string[:10],
                "%Y-%m-%d"
            ).replace(
                tzinfo=timezone.utc
            )

        except ValueError:

            return None


def days_old(date_string):

    posted = parse_date(
        date_string
    )

    if posted is None:
        return None

    now = datetime.now(
        timezone.utc
    )

    if posted.tzinfo is None:

        posted = posted.replace(
            tzinfo=timezone.utc
        )

    difference = (
        now - posted
    ).days

    return max(
        0,
        difference
    )


def create_fingerprint(job):

    company = clean_text(
        job["company"]
    ).lower()

    title = clean_text(
        job["title"]
    ).lower()

    location = clean_text(
        job["location"]
    ).lower()

    raw = "|".join([
        company,
        title,
        location
    ])

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def process_jobs(jobs, config):

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

    processed = []

    for job in jobs:

        # Clean common fields
        # while preserving all other
        # collector-specific fields.

        for field in [
            "title",
            "company",
            "location",
            "description",
            "url",
            "posted_date",
            "city",
            "region",
            "country",
            "department",
            "team",
            "workplace_type",
            "employment_type",
            "compensation",
            "apply_url"
        ]:

            job[field] = clean_text(
                job.get(field, "")
            )

        title = job["title"]

        description = job[
            "description"
        ]

        full_text = (
            title
            + " "
            + description
        )

        # -------------------------
        # Role matching
        # -------------------------

        role_match = any(
            contains_word(
                title,
                role
            )
            for role in roles
        )

        if not role_match:
            continue

        # -------------------------
        # Location matching
        # -------------------------

        location_match = any(
            location.lower()
            in job["location"].lower()
            for location in locations
        )

        if not location_match:
            continue

        # -------------------------
        # Exclusion
        # -------------------------

        title_excluded = any(
            contains_word(
                title,
                word
            )
            for word in exclude_words
        )

        if title_excluded:
            continue

        # -------------------------
        # Skills
        # -------------------------

        matched_required = [
            skill
            for skill in required_skills
            if contains_word(
                full_text,
                skill
            )
        ]

        matched_preferred = [
            skill
            for skill in preferred_skills
            if contains_word(
                full_text,
                skill
            )
        ]

        # At least ONE core skill.
        # Scoring decides how strong
        # the match is.

        if not matched_required:
            continue

        # -------------------------
        # Freshness
        # -------------------------

        age = days_old(
            job["posted_date"]
        )

        if (
            age is not None
            and age > max_days_old
        ):
            continue

        job[
            "required_skills"
        ] = matched_required

        job[
            "preferred_skills"
        ] = matched_preferred

        job[
            "age_days"
        ] = age

        job[
            "fingerprint"
        ] = create_fingerprint(
            job
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

            job[
                "duplicate_count"
            ] = 0

            unique[
                fingerprint
            ] = job

        else:

            unique[
                fingerprint
            ][
                "duplicate_count"
            ] += 1

    return list(
        unique.values()
    )
