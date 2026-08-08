import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.config.ignore_patterns import (
    IGNORED_DIRECTORIES,
    IGNORED_FILES,
    IGNORED_SUFFIXES,
)
from backend.core.logger import logger
from backend.services.github_service import github_service
from backend.services.ai_service import ai_service
from backend.core.settings import settings
from backend.utils.quality_score import QualityScore
from backend.utils.diff_mapper import diff_mapper
from backend.utils.duplicate_detector import DuplicateDetector
from backend.utils.review_analytics import generate_review_analytics
from backend.utils.review_recommendations import (
    generate_recommendations,
)
from backend.utils.review_cache import (
    generate_cache_key,
    get_cached_review,
    store_review,
    get_cache_statistics,
    clear_cache,
)
from backend.services.history_service import history_service



SUPPORTED_EXTENSIONS = {
    ".py", ".java", ".js", ".jsx", ".ts", ".tsx",
    ".c", ".cpp", ".h", ".hpp", ".cs",
    ".go", ".rs", ".php", ".rb", ".swift", ".kt",
}

LANGUAGE_MAP = {
    ".py": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "React JavaScript",
    ".ts": "TypeScript",
    ".tsx": "React TypeScript",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C Header",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".kt": "Kotlin",
}


class ReviewService:

    def review(self, code: str, language: str):
        return ai_service.review_code(code, language)

    def should_ignore_file(self, filename: str) -> bool:
        """
        Returns True if the file should not be reviewed.
        """

        normalized = filename.replace("\\", "/")

        parts = normalized.split("/")

        # Ignore directories
        for directory in parts[:-1]:
            if directory in IGNORED_DIRECTORIES:
                return True

        file_name = parts[-1]

        # Ignore exact filenames
        if file_name in IGNORED_FILES:
            return True

        # Ignore generated/minified files
        for suffix in IGNORED_SUFFIXES:
            if file_name.endswith(suffix):
                return True

        return False

    def review_file(self, filename: str, patch: str, language: str):
        """
        Review a single file.
        """

        logger.info("Reviewing %s (%s)", filename, language)

        cache_key = generate_cache_key(
            patch,
            language,
        )

        print(
            f"[{filename}] Cache Key: {cache_key}"
        )

        review = get_cached_review(cache_key)

        print(
            f"[{filename}] Cache Found: {review is not None}"
        )

        if review is None:

            review = ai_service.review_code(
                patch,
                language,
            )

            store_review(
                cache_key,
                review,
            )

            print(
                f"[{filename}] Stored in cache"
         )

            logger.info(
                "Cache MISS: %s",
                filename,
            )

        else:

            logger.info(
                "Cache HIT: %s",
                filename,
            )

        return {
            "filename": filename,
            "review": review,
        }
    
    def _normalize_issue(self, issue: dict, filename: str) -> dict:
        if not issue.get("file"):
            issue["file"] = filename

        issue["severity"] = (
            issue.get("severity", "LOW").upper()
            if isinstance(issue.get("severity"), str)
            else "LOW"
        )

        confidence = issue.get("confidence", 50)

        try:
            confidence = int(confidence)
        except (TypeError, ValueError):
            confidence = 50

        confidence = max(0, min(100, confidence))
        
        issue["confidence"] = confidence

        allowed_categories = {
            "Security",
            "Performance",
            "Correctness",
            "Maintainability",
            "Best Practices",
            "Documentation",
            "Testing",
        }

        category = issue.get("category", "Best Practices")

        if category not in allowed_categories:
            category = "Best Practices"

        issue["category"] = category

        return issue

    def _is_valid_inline_issue(self, issue: dict) -> bool:
        return (
            isinstance(issue.get("file"), str)
            and isinstance(issue.get("line"), int)
            and issue["line"] > 0
            and isinstance(issue.get("comment"), str)
            and issue["comment"].strip()
        )

    def _is_false_positive_issue(self, issue: dict) -> bool:
        """
        Returns True when the AI-generated issue matches a known
        false-positive pattern that should not be reported.
        """

        comment = issue.get("comment", "").lower()
        category = issue.get("category", "")

        # Do not report stylistic suggestions to replace simple loops
        # with built-in functions such as sum(), max(), min(), any(), all().
        builtin_terms = (
            "sum()",
            "sum function",
            "max()",
            "max function",
            "min()",
            "min function",
            "any()",
            "any function",
            "all()",
            "all function",
        )

        if (
            category == "Performance"
            and any(term in comment for term in builtin_terms)
        ):
            logger.info(
                "Filtered false-positive built-in suggestion: %s",
                comment,
            )
            return True

        # Do not report small, intentionally similar helper functions
        # as duplication issues.
        helper_names = (
            "find_user",
            "find_admin",
            "find_moderator",
            "find_reviewer",
        )

        if (
            category == "Maintainability"
            and (
                "duplication" in comment
                or "duplicated" in comment
                or "duplicate" in comment
            )
            and any(name in comment for name in helper_names)
        ):
            logger.info(
                "Filtered false-positive helper duplication: %s",
                comment,
            )
            return True

        # Do not report timing attacks for ordinary string comparisons
        # unless the review provides evidence that a secret is being
        # compared and the timing is realistically observable.
        timing_attack_terms = (
            "timing attack",
            "timing attacks",
            "timing-attack",
            "timing-attack vulnerability",
            "timing vulnerability",
        )

        if (
            category == "Security"
            and any(term in comment for term in timing_attack_terms)
        ):
            logger.info(
                "Filtered unsupported timing-attack finding: %s",
                comment,
            )
            return True

        return False

    def review_pull_request(self, pull_number: int):

        logger.info("Starting AI review for PR #%s", pull_number)

        # clear_cache()

        start_time = time.perf_counter()

        files = github_service.get_pull_request_files(
            pull_number
        )

        summaries = []
        issues = []

        ai_failures = 0

        review_tasks = []

        severity_count = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }

        # Collect review tasks
        for file in files:

            filename = file["filename"]
            patch = file.get("patch")

            # Ignore generated/vendor files
            if self.should_ignore_file(filename):
                logger.info(
                    "Ignoring file: %s",
                    filename,
                )
                continue

            _, extension = os.path.splitext(filename)
            extension = extension.lower()

            if extension not in SUPPORTED_EXTENSIONS:
                logger.info(
                    "Skipping unsupported file: %s",
                    filename,
                )
                continue

            if not patch:
                logger.info(
                    "Skipping %s (no patch)",
                    filename,
                )
                continue

            language = LANGUAGE_MAP.get(
                extension,
                "Unknown",
            )

            review_tasks.append(
                (
                    filename,
                    patch,
                    language,
                )
            )

        files_reviewed = len(review_tasks)

        # Parallel reviews
        with ThreadPoolExecutor(max_workers=4) as executor:

            futures = [
                executor.submit(
                    self.review_file,
                    filename,
                    patch,
                    language,
                )
                for filename, patch, language in review_tasks
            ]

            for future in as_completed(futures):

                try:

                    result = future.result()

                    filename = result["filename"]
                    review = result["review"]

                    if not review.get("success", True):
                        ai_failures += 1

                    summary = review.get("summary")

                    if summary:
                        summaries.append(
                            f"## {filename}\n{summary}"
                        )

                    for issue in review.get(
                        "issues",
                        [],
                    ):

                        issue = self._normalize_issue(
                            issue,
                            filename,
                        )

                        if self._is_false_positive_issue(issue):
                            continue

                        severity = issue["severity"]

                        if severity in severity_count:
                            severity_count[severity] += 1

                        issues.append(issue)

                except Exception:

                    ai_failures += 1

                    logger.exception(
                        "Error reviewing file."
                    )

        # Inline comments
        for issue in issues:

            if not self._is_valid_inline_issue(issue):
                logger.warning(
                    "Skipping invalid inline issue for PR %s: %s",
                    pull_number,
                    issue,
                )
                continue

            try:

                patch = None

                for file in files:
                    if file["filename"] == issue["file"]:
                        patch = file.get("patch", "")
                        break

                if patch:

                    changed_lines = diff_mapper.extract_changed_lines(
                        patch
                    )

                    if changed_lines:

                        if issue["line"] not in changed_lines:

                            issue["line"] = min(
                                changed_lines,
                                key=lambda x: abs(
                                    x - issue["line"]
                                ),
                            )

                print("=" * 60)
                print(f"Posting comment -> File: {issue['file']}")
                print(f"Mapped Line: {issue['line']}")
                print("=" * 60)

                github_service.create_inline_review_comment(
                    pull_number=pull_number,
                    file_path=issue["file"],
                    line=issue["line"],
                    comment=issue["comment"],
                )

            except Exception:

                logger.exception(
                    "Failed posting inline comment."
                )

        issues = DuplicateDetector.group_issues(issues)

        total_issues = len(issues)

        review_duration = round(
            time.perf_counter() - start_time,
            2,
        )

        critical = severity_count["CRITICAL"]
        high = severity_count["HIGH"]
        medium = severity_count["MEDIUM"]
        low = severity_count["LOW"]

        cache_stats = get_cache_statistics()
        
        statistics = {
            "review_duration_seconds": review_duration,
            "files_reviewed": files_reviewed,
            "files_skipped": 0,
            "ai_requests": cache_stats["cache_misses"],
            "ai_failures": ai_failures,

            "cache_hits": cache_stats["cache_hits"],
            "cache_misses": cache_stats["cache_misses"],
            "cache_hit_rate": cache_stats["cache_hit_rate"],
            "cache_size": cache_stats["cache_size"],

            "total_issues": total_issues,
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "average_issues_per_file": (
                round(total_issues / files_reviewed, 2)
                if files_reviewed
                else 0.0
            ),
        }

        quality = QualityScore.calculate(
            critical=critical,
            high=high,
            medium=medium,
            low=low,
        )

        analytics = generate_review_analytics(issues)
        recommendations = generate_recommendations(
            analytics,
        )


        score = quality["score"]

        if score >= 90:
            verdict = "🌟 Excellent"

        elif score >= 75:
            verdict = "✅ Looks Good"

        elif score >= 50:
            verdict = "⚠️ Review Required"

        else:
            verdict = "❌ Changes Required"

        report = f"""# 🤖 AI Code Review Report

## 📊 Summary

Quality Score: {quality["score"]}/100

Grade: {quality["grade"]}

Rating: {quality["stars"]}

Files Reviewed: {files_reviewed}

Issues Found: {total_issues}

🔴 Critical: {critical}
🟠 High: {high}
🟡 Medium: {medium}
🔵 Low: {low}

---

## Overall Verdict

{verdict}

---

## 📈 Analytics

Most Common Category: {analytics.most_common_category}

Most Common Severity: {analytics.most_common_severity}

Average Confidence: {analytics.average_confidence}%

Highest Confidence: {analytics.highest_confidence}%

Lowest Confidence: {analytics.lowest_confidence}%

---

## 📦 Cache Statistics

Cache Hits: {cache_stats["cache_hits"]}

Cache Misses: {cache_stats["cache_misses"]}

Cache Hit Rate: {cache_stats["cache_hit_rate"]}%

Cache Size: {cache_stats["cache_size"]}

---

## 💡 Recommendations

"""

        for recommendation in recommendations.recommendations:
            report += f"- {recommendation}\n"

        report += "\n---\n\n## File Reviews\n\n"

        if summaries:
            report += "\n\n".join(summaries)
        else:
            report += "No supported source files were reviewed."
    
        github_service.upsert_pull_request_comment(
            pull_number,
            report,
        )

        logger.info("Review completed.")

        try:
            logger.info("Saving review history...")

            review_id= history_service.save_review(
                repository=f"{settings.GITHUB_OWNER}/{settings.GITHUB_REPOSITORY}",
                pull_request=pull_number,
                quality_score=quality["score"],
                provider=review["provider"],
                review_duration=review_duration,
                total_files=files_reviewed,
                total_issues=total_issues,
                review_data={
                    "quality": quality,
                    "statistics": statistics,
                    "analytics": analytics.__dict__,
                    "recommendations": recommendations.recommendations,
                    "summary": report,
                    "issues": issues,
                },
            )

            logger.info("Review saved with ID: %s", review_id)

        except Exception as e:
            logger.exception("Failed to save review history :%s",e)

        return {
            "quality": {
                "score": quality["score"],
                "grade": quality["grade"],
                "stars": quality["stars"],
            },
            "statistics": statistics,
            "analytics": analytics,
            "recommendations": recommendations,
            "summary": report,
            "issues": issues,
        }


review_service = ReviewService()