"""
Phase 1 baseline runner.

Runs the existing AI review system against the E2E benchmark
files and sends the resulting findings to the evaluation engine.
"""

import json
import sys
from pathlib import Path


# Add project root to Python import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.services.ai_service import ai_service

from evaluator import (
    evaluate,
    load_ground_truth,
    print_report,
)


E2E_SOURCE_ROOT = Path(
    r"C:\Users\Win11\ai-review-test\e2e"
)

SOURCE_FILES = [
    ("security_cases.py", "Python"),
    ("safe_patterns.py", "Python"),
    ("correctness_cases.py", "Python"),
    ("maintainability_cases.py", "Python"),
]


def load_source_files() -> list[tuple[str, str, str]]:
    """Load benchmark source files."""

    sources = []

    for filename, language in SOURCE_FILES:

        path = E2E_SOURCE_ROOT / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Benchmark file not found: {path}"
            )

        code = path.read_text(
            encoding="utf-8"
        )

        sources.append(
            (
                filename,
                language,
                code,
            )
        )

    return sources


def run_ai_reviews() -> list[dict]:
    """Run the existing AI reviewer against every benchmark file."""

    findings = []

    sources = load_source_files()

    for filename, language, code in sources:

        print()
        print("=" * 60)
        print(f"Reviewing: {filename}")
        print("=" * 60)

        result = ai_service.review_code(
            code,
            language,
        )

        if not isinstance(result, dict):
            print(
                "WARNING: AI service returned "
                "an invalid response."
            )
            continue

        print(
            "Provider:",
            result.get("provider"),
        )

        print(
            "Success:",
            result.get("success"),
        )

        issues = result.get(
            "issues",
            [],
        )

        print(
            "Issues returned:",
            len(issues),
        )

        for issue in issues:

            finding = dict(issue)

            finding["file"] = (
                finding.get("file")
                or filename
            )

            findings.append(finding)

    return findings


def save_raw_findings(
    findings: list[dict],
) -> None:
    """Save raw AI findings for reproducibility."""

    report_directory = (
        Path(__file__).parent
        / "reports"
    )

    report_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        report_directory
        / "baseline_findings.json"
    )

    output_path.write_text(
        json.dumps(
            findings,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(
        f"Raw findings saved to: {output_path}"
    )


def main() -> None:
    """Run the Phase 1 baseline."""

    print()
    print("=" * 60)
    print("AI CODE REVIEW BOT — PHASE 1 BASELINE")
    print("=" * 60)

    ground_truth = load_ground_truth()

    findings = run_ai_reviews()

    save_raw_findings(findings)

    results = evaluate(
        ground_truth,
        findings,
    )

    print_report(results)


if __name__ == "__main__":
    main()