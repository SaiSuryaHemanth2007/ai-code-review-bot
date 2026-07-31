from pydantic import BaseModel
from typing import List


class RepositoryStatisticsItem(BaseModel):
    repository: str
    reviews: int
    average_quality: float
    files_reviewed: int
    issues_found: int


class RepositoryStatistics(BaseModel):
    repositories: List[RepositoryStatisticsItem]