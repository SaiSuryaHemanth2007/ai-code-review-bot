"""
Phase 1 evaluation engine for the AI Code Review Bot.

Compares ground-truth review cases against AI-generated findings
and calculates detection metrics.
"""

import json
from pathlib import Path


# Ground-truth benchmark belongs to this repository's
# evaluation directory.
GROUND_TRUTH_PATH = (
    Path(__file__).resolve().parent
    / "dataset"
    / "ground_truth.json"
)


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


def normalize(value: str | None) -> str:
    """Normalize text for deterministic matching."""

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .replace("\\", "/")
    )


def finding_matches_case(
    finding: dict,
    case: dict,
) -> bool:
    """
    Determine whether an AI finding corresponds to a
    ground-truth case.

    Phase 1 currently uses deterministic file + category
    matching. More precise semantic and line-aware matching
    can be introduced in later evaluation improvements.
    """

    finding_file = normalize(
        finding.get("file")
    )

    case_file = normalize(
        case.get("file")
    )

    finding_category = normalize(
        finding.get("category")
    )

    case_category = normalize(
        case.get("category")
    )

    return (
        finding_file == case_file
        and finding_category == case_category
    )


def evaluate(
    ground_truth: list[dict],
    findings: list[dict],
) -> dict:
    """
    Calculate TP, FP, and FN for supplied AI findings.

    Expected-positive cases are matched against AI findings.

    Expected-negative cases are treated as false-positive
    targets when the AI produces a finding for the same
    file/category.
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

    false_positive_findings: list[dict] = []

    for finding in findings:

        positive_match = next(
            (
                case
                for case in positive_cases
                if finding_matches_case(
                    finding,
                    case,
                )
            ),
            None,
        )

        if positive_match is not None:
            matched_positive_ids.add(
                positive_match["id"]
            )
            continue

        negative_match = next(
            (
                case
                for case in negative_cases
                if finding_matches_case(
                    finding,
                    case,
                )
            ),
            None,
        )

        if negative_match is not None:
            false_positive_findings.append(
                {
                    "finding": finding,
                    "case_id": negative_match["id"],
                }
            )
            continue

        false_positive_findings.append(
            {
                "finding": finding,
                "case_id": None,
            }
        )

    true_positive = len(
        matched_positive_ids
    )

    false_negative_cases = [
        case
        for case in positive_cases
        if case["id"] not in matched_positive_ids
    ]

    false_negative = len(
        false_negative_cases
    )

    false_positive = len(
        false_positive_findings
    )

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
        "total_cases": len(ground_truth),
        "positive_cases": len(positive_cases),
        "negative_cases": len(negative_cases),
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_findings": (
            false_positive_findings
        ),
        "false_negative_cases": (
            false_negative_cases
        ),
    }


def print_report(results: dict) -> None:
    """Print a human-readable evaluation report."""

    print()

    print("=" * 60)
    print(
        "AI CODE REVIEW BOT — PHASE 1 EVALUATION"
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

    print()

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

    print("=" * 60)


def main() -> None:
    """Run the evaluation engine."""

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