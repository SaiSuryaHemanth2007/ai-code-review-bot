"""
SQLite database for persistent review cache.
"""

import json
import sqlite3
from pathlib import Path

from backend.core.logger import logger

# Database location
DB_DIR = Path("backend/data")
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "review_cache.db"


class CacheDatabase:
    """SQLite wrapper for persistent review cache."""

    def __init__(self):
        self.db_path = DB_PATH
        self._initialize_database()

    def _get_connection(self):
        """Create a SQLite connection."""
        return sqlite3.connect(self.db_path)

    def _initialize_database(self):
        """Create the cache table if it doesn't exist."""

        with self._get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS review_cache (
                    cache_key TEXT PRIMARY KEY,
                    review TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.commit()

        logger.info(
            "SQLite review cache initialized: %s",
            self.db_path,
        )

    def get_review(self, cache_key: str):
        """
        Retrieve a cached review.

        Returns:
            dict | None
        """

        with self._get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT review
                FROM review_cache
                WHERE cache_key = ?
                """,
                (cache_key,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return json.loads(row[0])

    def store_review(
        self,
        cache_key: str,
        review: dict,
    ):
        """
        Store or replace a cached review.
        """

        with self._get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO review_cache
                (
                    cache_key,
                    review
                )
                VALUES (?, ?)
                """,
                (
                    cache_key,
                    json.dumps(review),
                ),
            )

            conn.commit()

    def delete_review(self, cache_key: str):
        """Delete one cached review."""

        with self._get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM review_cache
                WHERE cache_key = ?
                """,
                (cache_key,),
            )

            conn.commit()

    def clear_cache(self):
        """Remove every cached review."""

        with self._get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM review_cache
                """
            )

            conn.commit()

        logger.info("SQLite cache cleared.")

    def get_cache_size(self):
        """Return the number of cached reviews."""

        with self._get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM review_cache
                """
            )

            return cursor.fetchone()[0]


cache_db = CacheDatabase()