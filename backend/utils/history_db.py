import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class HistoryDatabase:
    """SQLite database for storing AI code review history."""

    def __init__(self):
        data_dir = Path("backend/data")
        data_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = data_dir / "review_history.db"
        self._initialize_database()

    def _get_connection(self):
        """Create a new SQLite connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_database(self):
        """Create the review_history table if it doesn't exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS review_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repository TEXT NOT NULL,
                    pull_request INTEGER NOT NULL,
                    quality_score REAL NOT NULL,
                    provider TEXT NOT NULL,
                    review_duration REAL NOT NULL,
                    total_files INTEGER NOT NULL,
                    total_issues INTEGER NOT NULL,
                    review_data TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_review(
        self,
        repository: str,
        pull_request: int,
        quality_score: float,
        provider: str,
        review_duration: float,
        total_files: int,
        total_issues: int,
        review_data: Dict
    ) -> int:
        """Save a completed review."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO review_history (
                    repository,
                    pull_request,
                    quality_score,
                    provider,
                    review_duration,
                    total_files,
                    total_issues,
                    review_data,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    repository,
                    pull_request,
                    quality_score,
                    provider,
                    review_duration,
                    total_files,
                    total_issues,
                    json.dumps(review_data, default=str),
                    datetime.utcnow().isoformat()
                )
            )
            conn.commit()
            return cursor.lastrowid

    def get_all_reviews(self) -> List[Dict]:
        """Return all reviews."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM review_history
                ORDER BY id DESC
                """
            ).fetchall()

            reviews = []

            for row in rows:
                item = dict(row)
                item["review_data"] = json.loads(item["review_data"])
                reviews.append(item)

            return reviews

    def get_review(self, review_id: int) -> Optional[Dict]:
        """Return a review by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM review_history
                WHERE id = ?
                """,
                (review_id,)
            ).fetchone()

            if row is None:
                return None

            item = dict(row)
            item["review_data"] = json.loads(item["review_data"])
            return item

    def delete_review(self, review_id: int) -> bool:
        """Delete a review."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                DELETE FROM review_history
                WHERE id = ?
                """,
                (review_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_statistics(self) -> Dict:
        """Return aggregated review statistics."""
        with self._get_connection() as conn:
            stats = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_reviews,
                    AVG(quality_score) AS average_score,
                    MAX(quality_score) AS highest_score,
                    MIN(quality_score) AS lowest_score,
                    AVG(review_duration) AS average_duration
                FROM review_history
                """
            ).fetchone()

            provider = conn.execute(
                """
                SELECT provider, COUNT(*) AS count
                FROM review_history
                GROUP BY provider
                ORDER BY count DESC
                LIMIT 1
                """
            ).fetchone()

            return {
                "total_reviews": stats["total_reviews"] or 0,
                "average_score": round(stats["average_score"] or 0, 2),
                "highest_score": stats["highest_score"] or 0,
                "lowest_score": stats["lowest_score"] or 0,
                "average_duration": round(stats["average_duration"] or 0, 2),
                "most_used_provider": provider["provider"] if provider else None
            }


history_db = HistoryDatabase()