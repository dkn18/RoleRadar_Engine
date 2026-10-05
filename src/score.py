def calculate_relevance(job):

    score = 0

    # -------------------------
    # Role match
    # -------------------------

    score += 30

    # -------------------------
    # Required skills
    # -------------------------

    required_count = len(
        job["required_skills"]
    )

    if required_count >= 2:

        score += 30

    elif required_count == 1:

        score += 15

    # -------------------------
    # Preferred skills
    # -------------------------

    preferred_count = len(
        job["preferred_skills"]
    )

    score += min(
        preferred_count * 4,
        20
    )

    # -------------------------
    # Location
    # -------------------------

    if job["location"]:

        score += 10

    # -------------------------
    # Freshness
    # -------------------------

    age = job["age_days"]

    if age is None:

        score += 2

    elif age <= 2:

        score += 10

    elif age <= 5:

        score += 8

    elif age <= 10:

        score += 6

    else:

        score += 3

    return min(
        score,
        100
    )


def calculate_hiring_confidence(job):

    score = 0

    # Company identified
    if job["company"]:
        score += 20

    # Direct application URL
    if job["url"]:
        score += 20

    # Recent posting
    age = job["age_days"]

    if age is not None:

        if age <= 3:
            score += 30

        elif age <= 7:
            score += 20

        elif age <= 14:
            score += 10

    # Description quality
    description_length = len(
        job["description"]
    )

    if description_length >= 500:

        score += 30

    elif description_length >= 250:

        score += 20

    elif description_length >= 100:

        score += 10

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
            "Missing URL"
        )

    if len(
        job["description"]
    ) < 150:

        score += 20

        warnings.append(
            "Short description"
        )

    age = job["age_days"]

    if (
        age is not None
        and age > 14
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
        ] = (
            calculate_hiring_confidence(
                job
            )
        )

        (
            red_score,
            warnings
        ) = calculate_red_flags(
            job
        )

        job[
            "red_flags"
        ] = red_score

        job[
            "warnings"
        ] = warnings

        # -------------------------
        # Recommendation
        # -------------------------

        if (
            job["relevance"] >= 75
            and
            job[
                "hiring_confidence"
            ] >= 70
            and
            job["red_flags"] <= 20
        ):

            job[
                "action"
            ] = "APPLY"

        elif (
            job["relevance"] >= 60
            and
            job["red_flags"] <= 40
        ):

            job[
                "action"
            ] = "VERIFY"

        else:

            job[
                "action"
            ] = "SKIP"

    return sorted(
        jobs,
        key=lambda job: (
            job["relevance"],
            job["hiring_confidence"],
            -job["red_flags"]
        ),
        reverse=True
    )
