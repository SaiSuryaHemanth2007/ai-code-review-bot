from backend.utils.cache_db import CacheDatabase


def test_store_and_get_review(tmp_path):
    db = CacheDatabase(
        tmp_path / "test_cache.db"
    )

    key = "pytest-review"

    review = {
        "summary": "Test Review",
        "issues": [],
    }

    db.store_review(
        key,
        review,
    )

    cached = db.get_review(key)

    assert cached == review


def test_delete_review(tmp_path):
    db = CacheDatabase(
        tmp_path / "test_cache.db"
    )

    key = "pytest-delete"

    db.store_review(
        key,
        {
            "summary": "Delete",
            "issues": [],
        },
    )

    db.delete_review(key)

    assert db.get_review(key) is None
