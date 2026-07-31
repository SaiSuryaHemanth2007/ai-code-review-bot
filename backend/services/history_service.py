from typing import Dict, List, Optional

from backend.utils.history_db import history_db


class HistoryService:
    """Service layer for review history."""

    def save_review(
        self,
        repository: str,
        pull_request: int,
        quality_score: float,
        provider: str,
        review_duration: float,
        total_files: int,
        total_issues: int,
        review_data: Dict,
    ) -> int:
        return history_db.save_review(
            repository=repository,
            pull_request=pull_request,
            quality_score=quality_score,
            provider=provider,
            review_duration=review_duration,
            total_files=total_files,
            total_issues=total_issues,
            review_data=review_data,
        )

    def get_all_reviews(self) -> List[Dict]:
        return history_db.get_all_reviews()

    def get_review(self, review_id: int) -> Optional[Dict]:
        return history_db.get_review(review_id)

    def delete_review(self, review_id: int) -> bool:
        return history_db.delete_review(review_id)

    def get_statistics(self) -> Dict:
        return history_db.get_statistics()


history_service = HistoryService()