"""
Schema for AI review recommendations.
"""

from typing import List

from pydantic import BaseModel


class ReviewRecommendations(BaseModel):
    recommendations: List[str]