"""
Simple thread-safe in-memory cache for AI reviews.
"""

import hashlib
from threading import Lock
from typing import Any, Optional

from backend.core.logger import logger

# Cache storage
review_cache: dict[str, Any] = {}

# Thread lock
cache_lock = Lock()

# Cache statistics
cache_hits = 0
cache_misses = 0

# Log after cache has been created
logger.info(
    "Review cache initialized. id=%s",
    id(review_cache),
)

print(f"Review cache initialized. Cache id={id(review_cache)}")


def generate_cache_key(code: str, language: str) -> str:
    """
    Generate a unique SHA-256 cache key using the
    file content and programming language.
    """
    content = f"{language}:{code}"
    key = hashlib.sha256(content.encode("utf-8")).hexdigest()

    print(
        f"Generated key={key[:8]} "
        f"language={language} "
        f"length={len(code)}"
    )

    return key


def get_cached_review(key: str) -> Optional[Any]:
    """
    Return cached review if available.
    Updates cache hit/miss statistics.
    """
    global cache_hits, cache_misses

    with cache_lock:

        print(
            f"Cache id={id(review_cache)} "
            f"size={len(review_cache)}"
        )

        review = review_cache.get(key)

        print(
            f"Lookup key={key[:8]} "
            f"found={review is not None}"
        )

        if review is not None:
            cache_hits += 1

            print(
                f"CACHE HIT "
                f"hits={cache_hits} "
                f"misses={cache_misses} "
                f"key={key[:8]}"
            )

            logger.info(
                "[CACHE HIT] hits=%s misses=%s key=%s",
                cache_hits,
                cache_misses,
                key[:8],
            )

        else:
            cache_misses += 1

            print(
                f"CACHE MISS "
                f"hits={cache_hits} "
                f"misses={cache_misses} "
                f"key={key[:8]}"
            )

            logger.info(
                "[CACHE MISS] hits=%s misses=%s key=%s",
                cache_hits,
                cache_misses,
                key[:8],
            )

        return review


def store_review(key: str, review: Any) -> None:
    """
    Store a review in the cache.
    """
    with cache_lock:

        review_cache[key] = review

        print(
            f"Stored key={key[:8]} "
            f"cache_size={len(review_cache)}"
        )

        logger.info(
            "Review stored in cache. Cache id=%s size=%s",
            id(review_cache),
            len(review_cache),
        )


def clear_cache() -> None:
    """
    Clear the entire cache.
    """
    global cache_hits, cache_misses

    with cache_lock:

        review_cache.clear()

        cache_hits = 0
        cache_misses = 0

        print(
            f"Cache cleared. "
            f"Cache id={id(review_cache)}"
        )

        logger.info(
            "Cache cleared. Cache id=%s",
            id(review_cache),
        )


def get_cache_size() -> int:
    """
    Return the number of cached reviews.
    """
    with cache_lock:
        return len(review_cache)


def get_cache_statistics() -> dict[str, float]:
    """
    Return cache statistics.
    """
    total_requests = cache_hits + cache_misses

    hit_rate = (
        (cache_hits / total_requests) * 100
        if total_requests > 0
        else 0.0
    )

    return {
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "cache_size": get_cache_size(),
        "cache_hit_rate": round(hit_rate, 2),
    }