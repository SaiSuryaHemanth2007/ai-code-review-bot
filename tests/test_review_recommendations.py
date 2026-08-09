from types import SimpleNamespace

from backend.utils.review_recommendations import generate_recommendations


def make_analytics(
    categories=None,
    severities=None,
):
    return SimpleNamespace(
        issues_by_category=categories or {},
        issues_by_severity=severities or {},
    )


def test_generates_security_recommendation():
    analytics = make_analytics(
        categories={"Security": 1},
    )

    result = generate_recommendations(analytics)

    assert (
        "Prioritize resolving security issues before merging."
        in result.recommendations[0]
    )


def test_generates_performance_recommendation():
    analytics = make_analytics(
        categories={"Performance": 1},
    )

    result = generate_recommendations(analytics)

    assert (
        "Optimize performance-related code paths."
        in result.recommendations[0]
    )


def test_generates_maintainability_recommendation():
    analytics = make_analytics(
        categories={"Maintainability": 1},
    )

    result = generate_recommendations(analytics)

    assert (
        "Refactor code to improve maintainability."
        in result.recommendations[0]
    )


def test_generates_documentation_recommendation():
    analytics = make_analytics(
        categories={"Documentation": 1},
    )

    result = generate_recommendations(analytics)

    assert (
        "Improve documentation and code comments."
        in result.recommendations[0]
    )


def test_generates_default_recommendation_when_no_categories():
    analytics = make_analytics()

    result = generate_recommendations(analytics)

    assert len(result.recommendations) == 1
    assert (
        "No major concerns found."
        in result.recommendations[0]
    )


def test_generates_multiple_recommendations():
    analytics = make_analytics(
        categories={
            "Security": 2,
            "Performance": 1,
            "Maintainability": 3,
            "Documentation": 1,
        },
    )

    result = generate_recommendations(analytics)

    assert len(result.recommendations) == 4

def test_generates_testing_recommendation():
    analytics = make_analytics(
        categories={"Testing": 1},
    )

    result = generate_recommendations(analytics)

    assert (
        "Increase test coverage before merging."
        in result.recommendations[0]
    )


def test_generates_severity_recommendation():
    analytics = make_analytics(
        severities={"HIGH": 1},
    )

    result = generate_recommendations(analytics)

    assert (
        "Resolve medium and higher severity issues before merging."
        in result.recommendations[0]
    )