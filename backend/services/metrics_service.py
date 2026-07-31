"""
Application metrics service.
"""

from backend.core.settings import settings
from backend.schemas.metrics_response import (
    MetricsResponse,
    ProviderMetrics,
)
from backend.services.providers.groq_provider import (
    groq_provider,
)
from backend.services.providers.gemini_provider import (
    gemini_provider,
)
from backend.utils.cache_db import cache_db


class MetricsService:
    """
    Returns runtime metrics for the application.
    """

    def get_metrics(self) -> MetricsResponse:

        total_reviews = cache_db.get_total_reviews()
        cached_reviews = cache_db.get_cached_reviews()

        cache_hit_rate = 0.0

        if total_reviews > 0:
            cache_hit_rate = round(
                (cached_reviews / total_reviews) * 100,
                2,
            )

        return MetricsResponse(
            total_reviews=total_reviews,
            cached_reviews=cached_reviews,
            cache_hit_rate=cache_hit_rate,
            providers=ProviderMetrics(
                Groq=(
                    "available"
                    if groq_provider.health_check()
                    else "unavailable"
                ),
                Gemini=(
                    "available"
                    if gemini_provider.health_check()
                    else "unavailable"
                ),
            ),
            version=settings.APP_VERSION,
        )


metrics_service = MetricsService()