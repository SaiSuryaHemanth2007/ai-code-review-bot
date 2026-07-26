from pydantic import BaseModel


class ReviewStatistics(BaseModel):
    review_duration_seconds: float
    files_reviewed: int
    files_skipped: int
    ai_requests: int
    ai_failures: int
    total_issues: int

    critical: int
    high: int
    medium: int
    low: int

    average_issues_per_file: float