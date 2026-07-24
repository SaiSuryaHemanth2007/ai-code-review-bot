import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.core.logger import logger
from backend.services.github_service import github_service
from backend.services.groq_service import groq_service


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
        return groq_service.review_code(code, language)

    def review_file(self, filename: str, patch: str, language: str):
        """
        Review a single file.
        """
        logger.info("Reviewing %s (%s)", filename, language)

        review = groq_service.review_code(
            patch,
            language,
        )

        return {
            "filename": filename,
            "review": review,
        }

    def review_pull_request(self, pull_number: int):

        logger.info("Starting AI review for PR #%s", pull_number)

        files = github_service.get_pull_request_files(pull_number)

        summaries = []
        issues = []

        review_tasks = []

        files_reviewed = 0

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

            _, extension = os.path.splitext(filename)
            extension = extension.lower()

            if extension not in SUPPORTED_EXTENSIONS:
                logger.info("Skipping %s (unsupported file)", filename)
                continue

            if not patch:
                logger.info("Skipping %s (no patch)", filename)
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

        # Review files in parallel
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

                    summary = review.get("summary")

                    if summary:
                        summaries.append(
                            f"## {filename}\n{summary}"
                        )

                    for issue in review.get("issues", []):

                        if not issue.get("file"):
                            issue["file"] = filename

                        severity = issue.get(
                            "severity",
                            "LOW",
                        ).upper()

                        if severity in severity_count:
                            severity_count[severity] += 1

                        issues.append(issue)

                except Exception:
                    logger.exception(
                        "Error reviewing file."
                    )

        # Post inline comments
        for issue in issues:

            try:

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

        total_issues = len(issues)

        if severity_count["CRITICAL"] > 0:
            verdict = "❌ Changes Required"
        elif severity_count["HIGH"] > 0:
            verdict = "⚠️ Review Required"
        else:
            verdict = "✅ Looks Good"

        report = f"""# 🤖 AI Code Review Report

## 📊 Summary

Files Reviewed: {files_reviewed}

Issues Found: {total_issues}

🔴 Critical: {severity_count['CRITICAL']}
🟠 High: {severity_count['HIGH']}
🟡 Medium: {severity_count['MEDIUM']}
🔵 Low: {severity_count['LOW']}

---

## Overall Verdict

{verdict}

---

## File Reviews

"""

        if summaries:
            report += "\n\n".join(summaries)
        else:
            report += "No supported source files were reviewed."

        github_service.upsert_pull_request_comment(
            pull_number,
            report,
        )

        logger.info("Review completed.")

        return {
            "summary": report,
            "issues": issues,
        }


review_service = ReviewService()