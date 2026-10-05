from process import (
    create_fingerprint,
    remove_duplicates
)

from score import (
    calculate_relevance,
    calculate_hiring_confidence
)


def test_fingerprint_same_job():

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

    job1 = {

        "company": "Example",

        "title": "Data Engineer",

        "location": "Amsterdam",

        "fingerprint": "abc123"
    }

    job2 = job1.copy()

    result = remove_duplicates(
        [
            job1,
            job2
        ]
    )

    assert len(result) == 1

    assert (
        result[0]["duplicate_count"]
        == 1
    )


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

    assert score >= 80


def test_hiring_confidence():

    job = {

        "company": "Example",

        "url": "https://example.com/job",

        "age_days": 1,

        "description": "x" * 500

    }

    score = calculate_hiring_confidence(
        job
    )

    assert score == 100
