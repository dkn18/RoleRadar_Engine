from process import (
    create_fingerprint,
    remove_duplicates
)

from score import (
    calculate_relevance
)


def test_fingerprint():

    job1 = {
        "company": "Example",
        "title": "Data Engineer",
        "location": "Amsterdam"
    }

    job2 = {
        "company": "Example",
        "title": "Data Engineer",
        "location": "Amsterdam"
    }

    assert (
        create_fingerprint(job1)
        ==
        create_fingerprint(job2)
    )


def test_duplicate_removal():

    job = {

        "company": "Example",

        "title": "Data Engineer",

        "location": "Amsterdam",

        "fingerprint": "123"

    }

    result = remove_duplicates(
        [
            job,
            job.copy()
        ]
    )

    assert len(result) == 1


def test_relevance():

    job = {

        "required_skills": [
            "Python",
            "SQL"
        ],

        "preferred_skills": [
            "Azure",
            "Databricks"
        ],

        "location": "Amsterdam",

        "age_days": 1

    }

    score = calculate_relevance(
        job
    )

    assert 0 <= score <= 100

    assert score >= 70
