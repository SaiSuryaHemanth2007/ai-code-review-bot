from pathlib import Path

import pytest

from backend.utils.history_db import HistoryDatabase


@pytest.fixture
def history_db(tmp_path: Path):
    """
    Create an isolated HistoryDatabase for testing.

    The real backend/data/review_history.db is never touched.
    """
    db = HistoryDatabase()

    db.db_path = tmp_path / "test_review_history.db"
    db._initialize_database()

    return db


def save_sample_review(
    db,
    repository="owner/repo",
    pull_request=1,
    quality_score=90,
    provider="Groq",
    review_duration=3.5,
    total_files=4,
    total_issues=2,
    review_data=None,
):
    """Helper for inserting a test review."""

    if review_data is None:
        review_data = {
            "summary": "Code looks good.",
            "issues": [],
        }

    return db.save_review(
        repository=repository,
        pull_request=pull_request,
        quality_score=quality_score,
        provider=provider,
        review_duration=review_duration,
        total_files=total_files,
        total_issues=total_issues,
        review_data=review_data,
    )


def test_database_initializes_table(history_db):
    """Database should create the review_history table."""

    with history_db._get_connection() as conn:
        result = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'review_history'
            """
        ).fetchone()

    assert result is not None
    assert result["name"] == "review_history"


def test_save_review_returns_id(history_db):
    """Saving a review should return its generated ID."""

    review_id = save_sample_review(history_db)

    assert isinstance(review_id, int)
    assert review_id > 0


def test_save_review_stores_all_fields(history_db):
    """Saved review should preserve all supplied review information."""

    review_data = {
        "summary": "Found one issue.",
        "issues": [
            {
                "severity": "HIGH",
                "comment": "Potential SQL injection.",
            }
        ],
    }

    review_id = save_sample_review(
        history_db,
        repository="test-owner/test-repo",
        pull_request=42,
        quality_score=92.5,
        provider="Gemini",
        review_duration=4.25,
        total_files=7,
        total_issues=1,
        review_data=review_data,
    )

    review = history_db.get_review(review_id)

    assert review is not None
    assert review["id"] == review_id
    assert review["repository"] == "test-owner/test-repo"
    assert review["pull_request"] == 42
    assert review["quality_score"] == 92.5
    assert review["provider"] == "Gemini"
    assert review["review_duration"] == 4.25
    assert review["total_files"] == 7
    assert review["total_issues"] == 1
    assert review["review_data"] == review_data
    assert review["created_at"]


def test_save_review_serializes_non_json_values(history_db):
    """Review data should be serializable using default=str."""

    review_data = {
        "timestamp": object(),
    }

    review_id = save_sample_review(
        history_db,
        review_data=review_data,
    )

    review = history_db.get_review(review_id)

    assert review is not None
    assert isinstance(review["review_data"]["timestamp"], str)


def test_get_all_reviews_returns_empty_list(history_db):
    """An empty database should return an empty list."""

    reviews = history_db.get_all_reviews()

    assert reviews == []


def test_get_all_reviews_returns_reviews_in_descending_id_order(
    history_db,
):
    """Reviews should be returned newest/highest ID first."""

    first_id = save_sample_review(
        history_db,
        pull_request=10,
    )

    second_id = save_sample_review(
        history_db,
        pull_request=20,
    )

    reviews = history_db.get_all_reviews()

    assert len(reviews) == 2
    assert reviews[0]["id"] == second_id
    assert reviews[1]["id"] == first_id
    assert reviews[0]["pull_request"] == 20
    assert reviews[1]["pull_request"] == 10


def test_get_review_returns_existing_review(history_db):
    """get_review should return the requested review."""

    review_id = save_sample_review(
        history_db,
        repository="owner/project",
        pull_request=99,
        quality_score=88,
    )

    review = history_db.get_review(review_id)

    assert review is not None
    assert review["id"] == review_id
    assert review["repository"] == "owner/project"
    assert review["pull_request"] == 99
    assert review["quality_score"] == 88


def test_get_review_returns_none_for_missing_review(history_db):
    """get_review should return None when the ID does not exist."""

    review = history_db.get_review(999999)

    assert review is None


def test_delete_review_returns_true_for_existing_review(
    history_db,
):
    """Deleting an existing review should return True."""

    review_id = save_sample_review(history_db)

    deleted = history_db.delete_review(review_id)

    assert deleted is True
    assert history_db.get_review(review_id) is None


def test_delete_review_returns_false_for_missing_review(
    history_db,
):
    """Deleting a missing review should return False."""

    deleted = history_db.delete_review(999999)

    assert deleted is False


def test_get_statistics_returns_zero_values_for_empty_database(
    history_db,
):
    """Statistics should return safe zero values when no reviews exist."""

    statistics = history_db.get_statistics()

    assert statistics == {
        "total_reviews": 0,
        "average_score": 0,
        "highest_score": 0,
        "lowest_score": 0,
        "average_duration": 0,
        "most_used_provider": None,
    }


def test_get_statistics_calculates_aggregates(history_db):
    """Statistics should correctly calculate review aggregates."""

    save_sample_review(
        history_db,
        quality_score=80,
        provider="Groq",
        review_duration=2.0,
    )

    save_sample_review(
        history_db,
        quality_score=90,
        provider="Groq",
        review_duration=4.0,
    )

    save_sample_review(
        history_db,
        quality_score=100,
        provider="Gemini",
        review_duration=6.0,
    )

    statistics = history_db.get_statistics()

    assert statistics["total_reviews"] == 3
    assert statistics["average_score"] == 90.0
    assert statistics["highest_score"] == 100
    assert statistics["lowest_score"] == 80
    assert statistics["average_duration"] == 4.0
    assert statistics["most_used_provider"] == "Groq"


def test_get_statistics_rounds_average_values(history_db):
    """Average score and duration should be rounded to two decimals."""

    save_sample_review(
        history_db,
        quality_score=91,
        review_duration=1.11,
    )

    save_sample_review(
        history_db,
        quality_score=92,
        review_duration=2.22,
    )

    save_sample_review(
        history_db,
        quality_score=94,
        review_duration=3.33,
    )

    statistics = history_db.get_statistics()

    assert statistics["average_score"] == 92.33
    assert statistics["average_duration"] == 2.22


def test_get_statistics_identifies_most_used_provider(
    history_db,
):
    """The provider with the most reviews should be selected."""

    save_sample_review(
        history_db,
        provider="Groq",
    )

    save_sample_review(
        history_db,
        provider="Gemini",
    )

    save_sample_review(
        history_db,
        provider="Groq",
    )

    save_sample_review(
        history_db,
        provider="Groq",
    )

    statistics = history_db.get_statistics()

    assert statistics["most_used_provider"] == "Groq"