"""
Utility for generating AI review recommendations.
"""

from backend.schemas.review_recommendations import (
    ReviewRecommendations,
)


def generate_recommendations(
    analytics,
) -> ReviewRecommendations:
    """
    Generate recommendations based on review analytics.
    """

    recommendations = []

    categories = analytics.issues_by_category
    severities = analytics.issues_by_severity

    if categories.get("Security", 0) > 0:
        recommendations.append(
            "🔒 Prioritize resolving security issues before merging."
        )

    if categories.get("Performance", 0) > 0:
        recommendations.append(
            "⚡ Optimize performance-related code paths."
        )

    if categories.get("Maintainability", 0) > 0:
        recommendations.append(
            "🛠️ Refactor code to improve maintainability."
        )

    if categories.get("Documentation", 0) > 0:
        recommendations.append(
            "📝 Improve documentation and code comments."
        )

    if categories.get("Testing", 0) > 0:
        recommendations.append(
            "🧪 Increase test coverage before merging."
        )

    if (
        severities.get("CRITICAL", 0) > 0
        or severities.get("HIGH", 0) > 0
        or severities.get("MEDIUM", 0) > 0
    ):
        recommendations.append(
            "⚠️ Resolve medium and higher severity issues before merging."
        )

    if not recommendations:
        recommendations.append(
            "✅ No major concerns found. The pull request is ready for review."
        )

    return ReviewRecommendations(
        recommendations=recommendations,
    )