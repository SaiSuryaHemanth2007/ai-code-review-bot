from pydantic import BaseModel
from typing import Dict


class ProviderStatisticsItem(BaseModel):
    reviews: int
    average_quality: float
    average_duration: float


class ProviderStatistics(BaseModel):
    providers: Dict[str, ProviderStatisticsItem]