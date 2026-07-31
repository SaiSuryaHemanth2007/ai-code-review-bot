from pydantic import BaseModel
from typing import Dict


class DashboardSummary(BaseModel):
    total_reviews: int
    average_quality_score: float
    total_files_reviewed: int
    total_issues_found: int
    average_review_duration: float
    repositories: int
    provider_usage: Dict[str, int]