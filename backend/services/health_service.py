"""
Health check service.
"""

from backend.core.settings import settings
from backend.schemas.health_response import (
    HealthResponse,
    ServiceStatus,
)
from backend.services.providers.groq_provider import (
    groq_provider,
)
from backend.services.providers.gemini_provider import (
    gemini_provider,
)


class HealthService:
    """
    Returns the application health status.
    """

    def get_health(self) -> HealthResponse:

        return HealthResponse(
            status="healthy",
            version=settings.APP_VERSION,
            services=ServiceStatus(
                groq=groq_provider.health_check(),
                gemini=gemini_provider.health_check(),
                cache=True,
                database=True,
                github=bool(
                    settings.GITHUB_TOKEN
                ),
            ),
        )


health_service = HealthService()