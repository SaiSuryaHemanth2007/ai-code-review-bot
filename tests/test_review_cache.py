from backend.utils.review_cache import (
    clear_cache,
    generate_cache_key,
    get_cached_review,
    get_cache_statistics,
    store_review,
)


def test_same_patch_and_language_generate_same_cache_key():
    key1 = generate_cache_key(
        "print('hello')",
        "python",
    )

    key2 = generate_cache_key(
        "print('hello')",
        "python",
    )

    assert key1 == key2


def test_different_patch_generates_different_cache_key():
    key1 = generate_cache_key(
        "print('hello')",
        "python",
    )

    key2 = generate_cache_key(
        "print('world')",
        "python",
    )

    assert key1 != key2


def test_different_language_generates_different_cache_key():
    key1 = generate_cache_key(
        "print('hello')",
        "python",
    )

    key2 = generate_cache_key(
        "print('hello')",
        "javascript",
    )

    assert key1 != key2


def test_cache_miss_is_counted():
    clear_cache()

    key = generate_cache_key(
        "missing review",
        "python",
    )

    assert get_cached_review(key) is None

    stats = get_cache_statistics()

    assert stats["cache_hits"] == 0
    assert stats["cache_misses"] == 1
    assert stats["cache_hit_rate"] == 0.0


def test_cache_hit_is_counted():
    clear_cache()

    key = generate_cache_key(
        "cached review",
        "python",
    )

    review = {
        "summary": "Cached Review",
        "issues": [],
    }

    store_review(key, review)

    assert get_cached_review(key) == review

    stats = get_cache_statistics()

    assert stats["cache_hits"] == 1
    assert stats["cache_misses"] == 0
    assert stats["cache_hit_rate"] == 100.0


def test_cache_hit_rate_is_calculated_correctly():
    clear_cache()

    key = generate_cache_key(
        "hit review",
        "python",
    )

    store_review(
        key,
        {
            "summary": "Review",
            "issues": [],
        },
    )

    get_cached_review(key)
    get_cached_review(key)

    missing_key = generate_cache_key(
        "missing review",
        "python",
    )

    get_cached_review(missing_key)

    stats = get_cache_statistics()

    assert stats["cache_hits"] == 2
    assert stats["cache_misses"] == 1
    assert stats["cache_hit_rate"] == 66.67


def test_clear_cache_resets_statistics():
    clear_cache()

    key = generate_cache_key(
        "temporary review",
        "python",
    )

    store_review(
        key,
        {
            "summary": "Temporary",
            "issues": [],
        },
    )

    get_cached_review(key)

    assert get_cache_statistics()["cache_hits"] == 1

    clear_cache()

    stats = get_cache_statistics()

    assert stats["cache_hits"] == 0
    assert stats["cache_misses"] == 0
    assert stats["cache_hit_rate"] == 0.0