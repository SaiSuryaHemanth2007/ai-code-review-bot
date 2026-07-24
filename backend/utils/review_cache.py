"""
Simple in-memory cache for AI reviews.
"""

import hashlib

review_cache = {}


def generate_cache_key(code: str, language: str) -> str:
    """
    Generate a unique cache key from code and language.
    """
    content = f"{language}:{code}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def get_cached_review(key: str):
    """
    Return cached review if available.
    """
    return review_cache.get(key)


def store_review(key: str, review: dict):
    """
    Store a review in the cache.
    """
    review_cache[key] = review