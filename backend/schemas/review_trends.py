from pydantic import BaseModel
from typing import List


class ReviewTrends(BaseModel):
    dates: List[str]
    review_counts: List[int]