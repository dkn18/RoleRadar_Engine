def calculate_relevance(job):

    score = 0

    # Role
    score += 30

    # Required skills
    if len(
        job["required_skills"]
    ) >= 2:

        score += 30

    # Preferred skills
    score += min(
        len(
            job["preferred_skills"]
        ) * 4,
        20
    )

    # Location
    if job["location"]:

        score += 10

    # Freshness
    if job["age_days"] is not None:

        if job["age_days"] <= 2:

            score += 10

        elif job["age_days"] <= 5:

            score += 7

        else:

            score += 4

    return min(
        score,
        100
    )


def calculate_hiring_confidence(job):

    score = 0

    if job["company"]:

        score += 25

    if job["url"]:

        score += 25

    if job["age_days"] is not None:

        if job["age_days"] <= 3:

            score += 25

        elif job["age_days"] <= 7:

            score += 15

    if len(
        job["description"]
    ) >= 300:

        score += 25

    elif len(
        job["description"]
    ) >= 150:

        score += 15

    return min(
        score,
        100
    )


def calculate_red_flags(job):

    score = 0

    warnings = []

    if not job["company"]:

        score += 30

        warnings.append(
            "Missing company"
        )

    if not job["url"]:

        score += 30

        warnings.append(
            "Missing job URL"
        )

    if len(
        job["description"]
    ) < 150:

        score += 20

        warnings.append(
            "Short description"
        )

    if (
        job["age_days"] is not None
        and job["age_days"] > 5
    ):

        score += 20

        warnings.append(
            "Older posting"
        )

    if job.get(
        "duplicate_count",
        0
    ) > 0:

        score += 10

        warnings.append(
            "Duplicate listing"
        )

    return min(
        score,
        100
    ), warnings


def score_jobs(jobs):

    for job in jobs:

        job["relevance"] = (
            calculate_relevance(
                job
            )
        )

        job[
            "hiring_confidence"
        ] = calculate_hiring_confidence(
            job
        )

        (
            red_score,
            warnings
        ) = calculate_red_flags(
            job
        )

        job["red_flags"] = (
            red_score
        )

        job["warnings"] = (
            warnings
        )

        if (
            job["relevance"] >= 75
            and
            job["hiring_confidence"] >= 70
            and
            job["red_flags"] <= 20
        ):

            job["action"] = "APPLY"

        elif job["red_flags"] <= 40:

            job["action"] = "VERIFY"

        else:

            job["action"] = "SKIP"

    return sorted(
        jobs,
        key=lambda job: (
            job["relevance"],
            job["hiring_confidence"],
            -job["red_flags"]
        ),
        reverse=True
    )
