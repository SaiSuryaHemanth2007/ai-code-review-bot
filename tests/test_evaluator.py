"""
Tests for the Phase 1 V2 evaluation engine.

These tests verify:

1. Basic detection
2. Category classification
3. Severity classification
4. False positives
5. False negatives
6. One-to-one matching
7. Per-category metrics
"""

from evaluation.evaluator import evaluate


def make_positive_case(
    case_id: str = "SEC-001",
    file: str = "security_cases.py",
    category: str = "Security",
    severity: str = "CRITICAL",
    description: str = "Hardcoded API key",
) -> dict:
    """Create a positive ground-truth case."""

    return {
        "id": case_id,
        "file": file,
        "category": category,
        "expected": True,
        "severity": severity,
        "description": description,
    }


def make_negative_case(
    case_id: str = "SAFE-001",
    file: str = "safe_patterns.py",
    category: str = "Security",
    description: str = "API key loaded from environment variable",
) -> dict:
    """Create a negative ground-truth case."""

    return {
        "id": case_id,
        "file": file,
        "category": category,
        "expected": False,
        "description": description,
    }


def make_finding(
    file: str = "security_cases.py",
    category: str = "Security",
    severity: str = "CRITICAL",
    comment: str = "Hardcoded API key is a security risk.",
    suggestion: str = "Store the API key in an environment variable.",
) -> dict:
    """Create an AI finding."""

    return {
        "file": file,
        "line": 3,
        "severity": severity,
        "category": category,
        "confidence": 95,
        "comment": comment,
        "suggestion": suggestion,
    }


# ---------------------------------------------------------------------------
# Detection tests
# ---------------------------------------------------------------------------


def test_exact_issue_detection():
    """An exact issue should be detected as a true positive."""

    ground_truth = [
        make_positive_case(),
    ]

    findings = [
        make_finding(),
    ]

    result = evaluate(
        ground_truth,
        findings,
    )

    assert result["true_positive"] == 1
    assert result["false_positive"] == 0
    assert result["false_negative"] == 0

    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1"] == 1.0


# ---------------------------------------------------------------------------
# Category classification
# ---------------------------------------------------------------------------


def test_detection_passes_when_category_is_wrong():
    """
    The underlying issue is detected even when the AI chooses
    the wrong category.

    Expected:
        Detection = PASS
        Category = FAIL
    """

    ground_truth = [
        make_positive_case(
            category="Correctness",
            severity="MEDIUM",
            description=(
                "Mutable default argument can retain state "
                "across function calls"
            ),
        ),
    ]

    findings = [
        make_finding(
            category="Best Practices",
            severity="MEDIUM",
            comment=(
                "The function uses a mutable default argument, "
                "which can retain state across calls."
            ),
            suggestion=(
                "Use None as the default argument and initialize "
                "the list inside the function."
            ),
        ),
    ]

    result = evaluate(
        ground_truth,
        findings,
    )

    # Detection should succeed.
    assert result["true_positive"] == 1

    # It should not be a false positive or false negative.
    assert result["false_positive"] == 0
    assert result["false_negative"] == 0

    # Classification should identify the wrong category.
    classification = result["classification"]

    assert classification["category_correct"] == 0
    assert classification["category_total"] == 1
    assert classification["category_accuracy"] == 0.0


# ---------------------------------------------------------------------------
# Severity classification
# ---------------------------------------------------------------------------


def test_detection_passes_when_severity_is_wrong():
    """
    The issue is detected correctly, but the severity is wrong.

    Expected:
        Detection = PASS
        Category = PASS
        Severity = FAIL
    """

    ground_truth = [
        make_positive_case(
            severity="CRITICAL",
        ),
    ]

    findings = [
        make_finding(
            severity="HIGH",
        ),
    ]

    result = evaluate(
        ground_truth,
        findings,
    )

    # Detection remains correct.
    assert result["true_positive"] == 1
    assert result["false_positive"] == 0
    assert result["false_negative"] == 0

    classification = result["classification"]

    # Category is correct.
    assert classification["category_correct"] == 1
    assert classification["category_accuracy"] == 1.0

    # Severity is incorrect.
    assert classification["severity_correct"] == 0
    assert classification["severity_total"] == 1
    assert classification["severity_accuracy"] == 0.0


# ---------------------------------------------------------------------------
# False-positive tests
# ---------------------------------------------------------------------------


def test_negative_case_reported_as_issue_is_false_positive():
    """
    If the benchmark explicitly says an issue should NOT exist
    and the AI reports it, the finding is a false positive.
    """

    ground_truth = [
        make_negative_case(),
    ]

    findings = [
        {
            "file": "safe_patterns.py",
            "line": 3,
            "severity": "HIGH",
            "category": "Security",
            "confidence": 90,
            "comment": (
                "The API key may be exposed."
            ),
            "suggestion": (
                "Move the API key to an environment variable."
            ),
        },
    ]

    result = evaluate(
        ground_truth,
        findings,
    )

    assert result["true_positive"] == 0
    assert result["false_positive"] == 1
    assert result["false_negative"] == 0

    assert result["precision"] == 0.0
    assert result["recall"] == 0.0
    assert result["f1"] == 0.0


# ---------------------------------------------------------------------------
# False-negative tests
# ---------------------------------------------------------------------------


def test_missing_positive_issue_is_false_negative():
    """
    If the benchmark expects an issue and the AI reports nothing,
    the case is a false negative.
    """

    ground_truth = [
        make_positive_case(),
    ]

    findings = []

    result = evaluate(
        ground_truth,
        findings,
    )

    assert result["true_positive"] == 0
    assert result["false_positive"] == 0
    assert result["false_negative"] == 1

    assert result["precision"] == 0.0
    assert result["recall"] == 0.0
    assert result["f1"] == 0.0

    assert len(
        result["false_negative_cases"]
    ) == 1

    assert (
        result["false_negative_cases"][0]["id"]
        == "SEC-001"
    )


# ---------------------------------------------------------------------------
# One-to-one matching
# ---------------------------------------------------------------------------


def test_one_ground_truth_case_cannot_match_twice():
    """
    Two AI findings describing the same issue must not produce
    two true positives for one ground-truth case.

    Expected:
        TP = 1
        FP = 1
    """

    ground_truth = [
        make_positive_case(),
    ]

    findings = [
        make_finding(
            comment=(
                "Hardcoded API key is a security risk."
            ),
        ),
        make_finding(
            comment=(
                "The API key is hardcoded and should "
                "be moved to secure configuration."
            ),
            suggestion=(
                "Use an environment variable."
            ),
        ),
    ]

    result = evaluate(
        ground_truth,
        findings,
    )

    assert result["true_positive"] == 1
    assert result["false_positive"] == 1
    assert result["false_negative"] == 0


# ---------------------------------------------------------------------------
# File isolation
# ---------------------------------------------------------------------------


def test_same_issue_in_different_file_is_not_a_match():
    """
    An issue with matching semantics but a different file should
    not match the benchmark case.
    """

    ground_truth = [
        make_positive_case(
            file="security_cases.py",
        ),
    ]

    findings = [
        make_finding(
            file="other_file.py",
        ),
    ]

    result = evaluate(
        ground_truth,
        findings,
    )

    assert result["true_positive"] == 0
    assert result["false_positive"] == 1
    assert result["false_negative"] == 1


# ---------------------------------------------------------------------------
# Per-category metrics
# ---------------------------------------------------------------------------


def test_per_category_metrics_are_calculated():
    """
    Verify that category-level detection metrics are produced.
    """

    ground_truth = [
        make_positive_case(
            case_id="SEC-001",
            category="Security",
            description="Hardcoded API key",
        ),
        make_positive_case(
            case_id="COR-001",
            file="correctness_cases.py",
            category="Correctness",
            severity="MEDIUM",
            description=(
                "Division by zero is possible when count is zero"
            ),
        ),
    ]

    findings = [
        make_finding(
            file="security_cases.py",
            category="Security",
            severity="CRITICAL",
            comment=(
                "Hardcoded API key is a security risk."
            ),
            suggestion=(
                "Use an environment variable."
            ),
        ),
        make_finding(
            file="correctness_cases.py",
            category="Correctness",
            severity="MEDIUM",
            comment=(
                "Division by zero is possible when count is zero."
            ),
            suggestion=(
                "Check whether count is zero."
            ),
        ),
    ]

    result = evaluate(
        ground_truth,
        findings,
    )

    category_metrics = result[
        "category_metrics"
    ]

    assert "security" in category_metrics
    assert "correctness" in category_metrics

    assert (
        category_metrics["security"]["f1"]
        == 1.0
    )

    assert (
        category_metrics["correctness"]["f1"]
        == 1.0
    )


# ---------------------------------------------------------------------------
# Classification details
# ---------------------------------------------------------------------------


def test_true_positive_match_contains_classification_details():
    """
    Every matched finding should expose detection,
    category and severity evaluation details.
    """

    ground_truth = [
        make_positive_case(),
    ]

    findings = [
        make_finding(),
    ]

    result = evaluate(
        ground_truth,
        findings,
    )

    assert len(
        result["true_positive_matches"]
    ) == 1

    match = result[
        "true_positive_matches"
    ][0]

    assert match["detection"] is True
    assert match["category_correct"] is True
    assert match["severity_correct"] is True
    assert match["case_id"] == "SEC-001"