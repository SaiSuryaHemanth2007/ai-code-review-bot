"""
Phase 1 evaluation engine for the AI Code Review Bot.

V2 introduces separate evaluation of:

1. Detection
   - Did the AI identify the underlying issue?

2. Classification
   - Did the AI assign the correct category?
   - Did the AI assign the correct severity?

The evaluator uses deterministic matching only.
It does not call another LLM or embedding model.

This keeps Phase 1 evaluation reproducible and
independent from another AI system.
"""

import json
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

GROUND_TRUTH_PATH = (
    Path(__file__).resolve().parent
    / "dataset"
    / "ground_truth.json"
)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_ground_truth() -> list[dict]:
    """Load and validate the ground-truth benchmark."""

    with GROUND_TRUTH_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    cases = data.get("cases")

    if not isinstance(cases, list):
        raise ValueError(
            "Ground truth must contain a 'cases' list."
        )

    return cases


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize(value: str | None) -> str:
    """
    Normalize a value for deterministic comparison.

    Examples:

        'Security' -> 'security'
        'security_cases.py' -> 'security_cases.py'
        'security\\cases.py' -> 'security/cases.py'
    """

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .replace("\\", "/")
    )


def normalize_text(value: str | None) -> str:
    """
    Normalize free-form text.

    Punctuation is removed and whitespace is normalized.
    """

    value = normalize(value)

    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value,
    )

    return " ".join(value.split())


def tokenize(value: str | None) -> set[str]:
    """Convert text into normalized tokens."""

    text = normalize_text(value)

    if not text:
        return set()

    return set(text.split())


# ---------------------------------------------------------------------------
# Finding text
# ---------------------------------------------------------------------------

def finding_description(finding: dict) -> str:
    """
    Build the searchable text for an AI finding.

    The AI currently provides the main explanation through
    'comment' and remediation through 'suggestion'.
    """

    parts = [
        finding.get("comment"),
        finding.get("suggestion"),
    ]

    return " ".join(
        str(part)
        for part in parts
        if part
    )


# ---------------------------------------------------------------------------
# Similarity
# ---------------------------------------------------------------------------

def description_similarity(
    finding: dict,
    case: dict,
) -> float:
    """
    Calculate Jaccard token similarity between an AI finding
    and a ground-truth description.

    Jaccard similarity:

        intersection / union

    This is deterministic and does not require an LLM.
    """

    finding_tokens = tokenize(
        finding_description(finding)
    )

    case_tokens = tokenize(
        case.get("description")
    )

    if not finding_tokens or not case_tokens:
        return 0.0

    intersection = (
        finding_tokens & case_tokens
    )

    union = (
        finding_tokens | case_tokens
    )

    if not union:
        return 0.0

    return len(intersection) / len(union)


def important_keyword_similarity(
    finding: dict,
    case: dict,
) -> float:
    """
    Calculate similarity using important code-review concepts.

    This provides a second deterministic signal for cases where
    the AI uses different wording from the benchmark.
    """

    finding_tokens = tokenize(
        finding_description(finding)
    )

    case_tokens = tokenize(
        case.get("description")
    )

    if not finding_tokens or not case_tokens:
        return 0.0

    important_keywords = {
        # Security
        "api",
        "key",
        "hardcoded",
        "credential",
        "credentials",
        "administrator",
        "admin",
        "command",
        "commands",
        "execution",
        "execute",
        "injection",
        "shell",
        "system",
        "subprocess",
        "eval",
        "python",
        "dynamic",
        "code",
        "path",
        "traversal",
        "filename",
        "unsanitized",
        "user",
        "input",
        "password",

        # Correctness
        "division",
        "divide",
        "zero",
        "count",
        "mutable",
        "default",
        "argument",
        "state",
        "calls",
        "average",
        "empty",
        "list",

        # Maintainability
        "nested",
        "conditional",
        "readability",
        "debug",
        "print",
        "temporary",
        "variable",
        "production",
        "maintainability",
    }

    finding_keywords = (
        finding_tokens & important_keywords
    )

    case_keywords = (
        case_tokens & important_keywords
    )

    if not finding_keywords or not case_keywords:
        return 0.0

    intersection = (
        finding_keywords & case_keywords
    )

    union = (
        finding_keywords | case_keywords
    )

    if not union:
        return 0.0

    return len(intersection) / len(union)


# ---------------------------------------------------------------------------
# Structural matching
# ---------------------------------------------------------------------------

def file_matches(
    finding: dict,
    case: dict,
) -> bool:
    """Return True when the finding and case refer to the same file."""

    return (
        normalize(finding.get("file"))
        == normalize(case.get("file"))
    )


def finding_matches_case(
    finding: dict,
    case: dict,
) -> bool:
    """
    Determine whether an AI finding detects the same underlying
    issue as a ground-truth case.

    IMPORTANT:

    Category is intentionally NOT required here.

    This is the key V2 change.

    Example:

        Ground truth:
            category = Correctness
            description = Mutable default argument

        AI:
            category = Best Practices
            description = Mutable default argument

    Detection:
        PASS

    Classification:
        FAIL
    """

    if not file_matches(
        finding,
        case,
    ):
        return False

    description_score = description_similarity(
        finding,
        case,
    )

    keyword_score = important_keyword_similarity(
        finding,
        case,
    )

    # Strong textual similarity.
    if description_score >= 0.12:
        return True

    # Strong domain-specific keyword overlap.
    if keyword_score >= 0.20:
        return True

    return False


# ---------------------------------------------------------------------------
# Matching score
# ---------------------------------------------------------------------------

def matching_score(
    finding: dict,
    case: dict,
) -> float:
    """
    Calculate the score used to choose the best matching
    ground-truth case.
    """

    if not file_matches(
        finding,
        case,
    ):
        return -1.0

    description_score = description_similarity(
        finding,
        case,
    )

    keyword_score = important_keyword_similarity(
        finding,
        case,
    )

    return (
        description_score
        + keyword_score
    )


# ---------------------------------------------------------------------------
# Best-match selection
# ---------------------------------------------------------------------------

def find_best_positive_match(
    finding: dict,
    positive_cases: list[dict],
    matched_positive_ids: set[str],
) -> dict | None:
    """
    Find the best currently-unmatched positive case.

    Each ground-truth positive case can only be matched once.
    """

    candidates: list[tuple[float, dict]] = []

    for case in positive_cases:
        case_id = case.get("id")

        if case_id in matched_positive_ids:
            continue

        if not finding_matches_case(
            finding,
            case,
        ):
            continue

        score = matching_score(
            finding,
            case,
        )

        candidates.append(
            (
                score,
                case,
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return candidates[0][1]


def find_negative_match(
    finding: dict,
    negative_cases: list[dict],
) -> dict | None:
    """
    Find a negative benchmark case that the AI incorrectly
    reported as an issue.

    Negative cases are never counted as true positives.
    """

    candidates: list[tuple[float, dict]] = []

    for case in negative_cases:
        if not finding_matches_case(
            finding,
            case,
        ):
            continue

        score = matching_score(
            finding,
            case,
        )

        candidates.append(
            (
                score,
                case,
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return candidates[0][1]


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def category_matches(
    finding: dict,
    case: dict,
) -> bool:
    """Check whether AI category matches ground truth."""

    return (
        normalize(finding.get("category"))
        == normalize(case.get("category"))
    )


def severity_matches(
    finding: dict,
    case: dict,
) -> bool:
    """
    Check whether AI severity matches ground truth.

    If a positive benchmark case has no severity, it is not
    included in the severity accuracy denominator.
    """

    expected_severity = normalize(
        case.get("severity")
    )

    actual_severity = normalize(
        finding.get("severity")
    )

    if not expected_severity:
        return None

    return (
        actual_severity == expected_severity
    )


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------

def calculate_metrics(
    true_positive: int,
    false_positive: int,
    false_negative: int,
) -> dict:
    """Calculate precision, recall and F1."""

    precision_denominator = (
        true_positive
        + false_positive
    )

    recall_denominator = (
        true_positive
        + false_negative
    )

    precision = (
        true_positive
        / precision_denominator
        if precision_denominator
        else 0.0
    )

    recall = (
        true_positive
        / recall_denominator
        if recall_denominator
        else 0.0
    )

    f1_denominator = (
        precision
        + recall
    )

    f1 = (
        2 * precision * recall
        / f1_denominator
        if f1_denominator
        else 0.0
    )

    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


# ---------------------------------------------------------------------------
# Per-category metrics
# ---------------------------------------------------------------------------

def calculate_category_metrics(
    positive_cases: list[dict],
    true_positive_matches: list[dict],
    false_positive_findings: list[dict],
) -> dict:
    """
    Calculate detection metrics for each expected-positive
    category.

    A finding matched to a positive case contributes to that
    case's category.

    Unmatched findings are attributed to the category they
    actually reported when possible.
    """

    categories = sorted(
        {
            normalize(case.get("category"))
            for case in positive_cases
            if case.get("category")
        }
    )

    results: dict[str, dict] = {}

    for category in categories:
        category_positive_cases = [
            case
            for case in positive_cases
            if normalize(
                case.get("category")
            ) == category
        ]

        category_matches = [
            match
            for match in true_positive_matches
            if normalize(
                match["case"].get("category")
            ) == category
        ]

        matched_ids = {
            match["case"]["id"]
            for match in category_matches
        }

        category_false_negatives = [
            case
            for case in category_positive_cases
            if case["id"] not in matched_ids
        ]

        category_false_positives = [
            item
            for item in false_positive_findings
            if normalize(
                item["finding"].get("category")
            ) == category
        ]

        metrics = calculate_metrics(
            true_positive=len(category_matches),
            false_positive=len(
                category_false_positives
            ),
            false_negative=len(
                category_false_negatives
            ),
        )

        results[category] = metrics

    return results


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate(
    ground_truth: list[dict],
    findings: list[dict],
) -> dict:
    """
    Evaluate AI findings against the benchmark.

    V2 evaluation has two independent dimensions:

    Detection:
        Did the AI identify the underlying issue?

    Classification:
        Did the AI assign the correct category?
        Did the AI assign the correct severity?

    Detection does NOT require category to match.
    This allows us to distinguish:

        "issue missed"

    from:

        "issue detected but classified incorrectly."
    """

    positive_cases = [
        case
        for case in ground_truth
        if case.get("expected") is True
    ]

    negative_cases = [
        case
        for case in ground_truth
        if case.get("expected") is False
    ]

    matched_positive_ids: set[str] = set()

    true_positive_matches: list[dict] = []

    false_positive_findings: list[dict] = []

    # ------------------------------------------------------------------
    # Match every AI finding against the positive benchmark cases.
    # ------------------------------------------------------------------

    for finding in findings:
        positive_match = find_best_positive_match(
            finding,
            positive_cases,
            matched_positive_ids,
        )

        if positive_match is not None:
            case_id = positive_match["id"]

            matched_positive_ids.add(
                case_id
            )

            category_correct = category_matches(
                finding,
                positive_match,
            )

            severity_correct = severity_matches(
                finding,
                positive_match,
            )

            true_positive_matches.append(
                {
                    "finding": finding,
                    "case": positive_match,
                    "case_id": case_id,
                    "score": matching_score(
                        finding,
                        positive_match,
                    ),
                    "detection": True,
                    "category_correct": (
                        category_correct
                    ),
                    "severity_correct": (
                        severity_correct
                    ),
                }
            )

            continue

        # --------------------------------------------------------------
        # If the finding does not detect a positive case, check whether
        # it incorrectly reports a negative/safe benchmark case.
        # --------------------------------------------------------------

        negative_match = find_negative_match(
            finding,
            negative_cases,
        )

        if negative_match is not None:
            false_positive_findings.append(
                {
                    "finding": finding,
                    "case": negative_match,
                    "case_id": negative_match["id"],
                    "reason": "matched_negative_case",
                }
            )

            continue

        # --------------------------------------------------------------
        # Finding does not correspond to any benchmark case.
        # --------------------------------------------------------------

        false_positive_findings.append(
            {
                "finding": finding,
                "case": None,
                "case_id": None,
                "reason": "unmatched_finding",
            }
        )

    # ------------------------------------------------------------------
    # False negatives
    # ------------------------------------------------------------------

    false_negative_cases = [
        case
        for case in positive_cases
        if case["id"] not in matched_positive_ids
    ]

    # ------------------------------------------------------------------
    # Detection metrics
    # ------------------------------------------------------------------

    detection_metrics = calculate_metrics(
        true_positive=len(
            true_positive_matches
        ),
        false_positive=len(
            false_positive_findings
        ),
        false_negative=len(
            false_negative_cases
        ),
    )

    # ------------------------------------------------------------------
    # Classification metrics
    # ------------------------------------------------------------------

    category_total = len(
        true_positive_matches
    )

    category_correct_count = sum(
        1
        for match in true_positive_matches
        if match["category_correct"]
    )

    category_accuracy = (
        category_correct_count
        / category_total
        if category_total
        else 0.0
    )

    severity_matches_with_expected = [
        match
        for match in true_positive_matches
        if match["severity_correct"] is not None
    ]

    severity_total = len(
        severity_matches_with_expected
    )

    severity_correct_count = sum(
        1
        for match in severity_matches_with_expected
        if match["severity_correct"]
    )

    severity_accuracy = (
        severity_correct_count
        / severity_total
        if severity_total
        else 0.0
    )

    classification_metrics = {
        "category_correct": (
            category_correct_count
        ),
        "category_total": category_total,
        "category_accuracy": category_accuracy,
        "severity_correct": (
            severity_correct_count
        ),
        "severity_total": severity_total,
        "severity_accuracy": severity_accuracy,
    }

    # ------------------------------------------------------------------
    # Per-category detection metrics
    # ------------------------------------------------------------------

    category_metrics = calculate_category_metrics(
        positive_cases=positive_cases,
        true_positive_matches=(
            true_positive_matches
        ),
        false_positive_findings=(
            false_positive_findings
        ),
    )

    # ------------------------------------------------------------------
    # Final result
    # ------------------------------------------------------------------

    return {
        # Existing V1-compatible metrics.
        "total_cases": len(ground_truth),
        "positive_cases": len(positive_cases),
        "negative_cases": len(negative_cases),
        "true_positive": detection_metrics[
            "true_positive"
        ],
        "false_positive": detection_metrics[
            "false_positive"
        ],
        "false_negative": detection_metrics[
            "false_negative"
        ],
        "precision": detection_metrics[
            "precision"
        ],
        "recall": detection_metrics[
            "recall"
        ],
        "f1": detection_metrics[
            "f1"
        ],

        # V2 detection metrics.
        "detection": detection_metrics,

        # V2 classification metrics.
        "classification": classification_metrics,

        # Per-category metrics.
        "category_metrics": category_metrics,

        # Detailed matches.
        "true_positive_matches": (
            true_positive_matches
        ),

        # Detailed false positives.
        "false_positive_findings": (
            false_positive_findings
        ),

        # Detailed false negatives.
        "false_negative_cases": (
            false_negative_cases
        ),
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(results: dict) -> None:
    """Print a human-readable Phase 1 V2 report."""

    print()

    print("=" * 60)
    print(
        "AI CODE REVIEW BOT — PHASE 1 V2 EVALUATION"
    )
    print("=" * 60)

    print(
        f"Total benchmark cases : "
        f"{results['total_cases']}"
    )

    print(
        f"Positive cases        : "
        f"{results['positive_cases']}"
    )

    print(
        f"Negative cases        : "
        f"{results['negative_cases']}"
    )

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    print()
    print("-" * 60)
    print("DETECTION")
    print("-" * 60)

    print(
        f"True Positives        : "
        f"{results['true_positive']}"
    )

    print(
        f"False Positives       : "
        f"{results['false_positive']}"
    )

    print(
        f"False Negatives       : "
        f"{results['false_negative']}"
    )

    print()

    print(
        f"Precision             : "
        f"{results['precision']:.2%}"
    )

    print(
        f"Recall                : "
        f"{results['recall']:.2%}"
    )

    print(
        f"F1 Score              : "
        f"{results['f1']:.2%}"
    )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    classification = results[
        "classification"
    ]

    print()
    print("-" * 60)
    print("CLASSIFICATION")
    print("-" * 60)

    print(
        f"Category Correct      : "
        f"{classification['category_correct']}"
        f"/"
        f"{classification['category_total']}"
    )

    print(
        f"Category Accuracy     : "
        f"{classification['category_accuracy']:.2%}"
    )

    print()

    print(
        f"Severity Correct      : "
        f"{classification['severity_correct']}"
        f"/"
        f"{classification['severity_total']}"
    )

    print(
        f"Severity Accuracy     : "
        f"{classification['severity_accuracy']:.2%}"
    )

    # ------------------------------------------------------------------
    # Per-category metrics
    # ------------------------------------------------------------------

    print()
    print("-" * 60)
    print("PER-CATEGORY DETECTION")
    print("-" * 60)

    for category, metrics in results[
        "category_metrics"
    ].items():

        display_category = (
            category.title()
        )

        print()
        print(
            f"{display_category}"
        )

        print(
            f"  Precision : "
            f"{metrics['precision']:.2%}"
        )

        print(
            f"  Recall    : "
            f"{metrics['recall']:.2%}"
        )

        print(
            f"  F1        : "
            f"{metrics['f1']:.2%}"
        )

    # ------------------------------------------------------------------
    # True positive matches
    # ------------------------------------------------------------------

    print()
    print("-" * 60)
    print("TRUE POSITIVE MATCHES")
    print("-" * 60)

    for match in results[
        "true_positive_matches"
    ]:

        category_status = (
            "PASS"
            if match["category_correct"]
            else "FAIL"
        )

        severity_status = (
            "N/A"
            if match["severity_correct"] is None
            else (
                "PASS"
                if match["severity_correct"]
                else "FAIL"
            )
        )

        print(
            f"{match['case_id']} "
            f"(score={match['score']:.3f}) "
            f"| Category={category_status} "
            f"| Severity={severity_status}"
        )

    # ------------------------------------------------------------------
    # False positives
    # ------------------------------------------------------------------

    print()
    print("-" * 60)
    print("FALSE POSITIVES")
    print("-" * 60)

    for item in results[
        "false_positive_findings"
    ]:

        finding = item["finding"]

        case_id = (
            item["case_id"]
            or "UNMATCHED"
        )

        print(
            f"{case_id} "
            f"— "
            f"{finding.get('file')} "
            f"line "
            f"{finding.get('line')} "
            f"— "
            f"{finding.get('category')} "
            f"— "
            f"{item['reason']}"
        )

    # ------------------------------------------------------------------
    # False negatives
    # ------------------------------------------------------------------

    print()
    print("-" * 60)
    print("FALSE NEGATIVES")
    print("-" * 60)

    for case in results[
        "false_negative_cases"
    ]:

        print(
            f"{case['id']} "
            f"— "
            f"{case['description']}"
        )

    print()
    print("=" * 60)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the evaluator in smoke-test mode."""

    ground_truth = load_ground_truth()

    # Smoke-test mode.
    #
    # The real AI findings are connected by
    # evaluation/run_baseline.py.
    findings: list[dict] = []

    results = evaluate(
        ground_truth,
        findings,
    )

    print_report(results)


if __name__ == "__main__":
    main()