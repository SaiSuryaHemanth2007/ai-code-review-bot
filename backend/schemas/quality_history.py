from pydantic import BaseModel
from typing import List


class QualityHistory(BaseModel):
    quality_scores: List[float]