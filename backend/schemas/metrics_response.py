from pydantic import BaseModel


class ProviderMetrics(BaseModel):
    Groq: str
    Gemini: str


class MetricsResponse(BaseModel):
    total_reviews: int
    cached_reviews: int
    cache_hit_rate: float
    providers: ProviderMetrics
    version: str