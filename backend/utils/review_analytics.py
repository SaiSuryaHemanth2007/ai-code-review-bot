"""
Utility for generating review analytics.
"""

from collections import Counter

from backend.schemas.review_analytics import ReviewAnalytics


def generate_review_analytics(issues: list) -> ReviewAnalytics:
    """
    Generate analytics from review issues.
    """

    category_counter = Counter()
    severity_counter = Counter()
    confidence_scores = []

    for issue in issues:

        category = issue.get("category", "Unknown")
        severity = issue.get("severity", "LOW")

        category_counter[category] += 1
        severity_counter[severity] += 1

        confidence = issue.get("confidence")

        if isinstance(confidence, (int, float)):
            confidence_scores.append(confidence)

    if confidence_scores:
        average_confidence = round(
            sum(confidence_scores) / len(confidence_scores),
            2,
        )
        highest_confidence = max(confidence_scores)
        lowest_confidence = min(confidence_scores)
    else:
        average_confidence = 0
        highest_confidence = 0
        lowest_confidence = 0

    most_common_category = (
        category_counter.most_common(1)[0][0]
        if category_counter
        else "None"
    )

    most_common_severity = (
        severity_counter.most_common(1)[0][0]
        if severity_counter
        else "None"
    )

    return ReviewAnalytics(
        issues_by_category=dict(category_counter),
        issues_by_severity=dict(severity_counter),
        average_confidence=average_confidence,
        highest_confidence=highest_confidence,
        lowest_confidence=lowest_confidence,
        most_common_category=most_common_category,
        most_common_severity=most_common_severity,
    )