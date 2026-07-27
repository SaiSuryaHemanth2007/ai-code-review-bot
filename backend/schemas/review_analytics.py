"""
Schema for review analytics.
"""

from typing import Dict

from pydantic import BaseModel


class ReviewAnalytics(BaseModel):
    issues_by_category: Dict[str, int]
    issues_by_severity: Dict[str, int]

    average_confidence: float
    highest_confidence: int
    lowest_confidence: int

    most_common_category: str
    most_common_severity: str