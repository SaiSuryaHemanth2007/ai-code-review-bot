"""
Persistent review cache backed by SQLite.
"""

import hashlib

from backend.core.logger import logger
from backend.utils.cache_db import cache_db

cache_hits = 0
cache_misses = 0


def generate_cache_key(
    patch: str,
    language: str,
) -> str:
    """
    Generate a deterministic cache key from the code patch
    and programming language.
    """

    content = f"{language}:{patch}"

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def get_cached_review(cache_key: str):
    """
    Retrieve a cached review.

    Returns:
        dict | None
    """

    global cache_hits
    global cache_misses

    review = cache_db.get_review(cache_key)

    if review is None:

        cache_misses += 1

        logger.info(
            "Cache MISS: %s",
            cache_key,
        )

        return None

    cache_hits += 1

    logger.info(
        "Cache HIT: %s",
        cache_key,
    )

    return review


def store_review(
    cache_key: str,
    review: dict,
):
    """
    Store a review in the cache.
    """

    cache_db.store_review(
        cache_key,
        review,
    )

    logger.info(
        "Stored review in cache: %s",
        cache_key,
    )


def clear_cache():
    """
    Remove every cached review.
    """

    global cache_hits
    global cache_misses

    cache_db.clear_cache()

    cache_hits = 0
    cache_misses = 0

    logger.info("Review cache cleared.")


def get_cache_statistics():
    """
    Return cache statistics.
    """

    total_requests = cache_hits + cache_misses

    hit_rate = (
        round(
            (cache_hits / total_requests) * 100,
            2,
        )
        if total_requests
        else 0.0
    )

    return {
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "cache_hit_rate": hit_rate,
        "cache_size": cache_db.get_cache_size(),
    }