from backend.utils.cache_db import cache_db


def test_store_and_get_review():

    key = "pytest-review"

    review = {
        "summary": "Test Review",
        "issues": [],
    }

    cache_db.store_review(
        key,
        review,
    )

    cached = cache_db.get_review(key)

    assert cached == review


def test_delete_review():

    key = "pytest-delete"

    cache_db.store_review(
        key,
        {
            "summary": "Delete",
            "issues": [],
        },
    )

    cache_db.delete_review(key)

    assert cache_db.get_review(key) is None