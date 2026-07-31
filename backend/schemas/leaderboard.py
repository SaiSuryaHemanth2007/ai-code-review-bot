from pydantic import BaseModel


class ReviewRecord(BaseModel):
    repository: str
    pull_request: int
    value: float


class Leaderboard(BaseModel):
    highest_quality_review: ReviewRecord
    fastest_review: ReviewRecord
    largest_review: ReviewRecord
    most_issues_found: ReviewRecord