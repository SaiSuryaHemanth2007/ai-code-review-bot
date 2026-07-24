import os

from backend.core.logger import logger
from backend.services.github_service import github_service
from backend.services.groq_service import groq_service


SUPPORTED_EXTENSIONS = {
    ".py",
    ".java",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
}


class ReviewService:
    """Coordinates the AI review process."""

    def review(self, code: str, language: str):
        """Review a code snippet."""
        return groq_service.review_code(code, language)

    def review_pull_request(self, pull_number: int):
        """Review an entire GitHub pull request."""

        logger.info("Starting AI review for PR #%s", pull_number)

        files = github_service.get_pull_request_files(pull_number)

        all_summaries = []
        all_issues = []

        for file in files:

            filename = file["filename"]
            patch = file.get("patch")

            # Skip unsupported file types
            _, extension = os.path.splitext(filename)

            if extension.lower() not in SUPPORTED_EXTENSIONS:
                logger.info(
                    "Skipping %s (unsupported file type).",
                    filename,
                )
                continue

            # Skip deleted/binary files
            if not patch:
                logger.info(
                    "Skipping %s (no patch available).",
                    filename,
                )
                continue

            logger.info("Reviewing file: %s", filename)

            review = groq_service.review_code(
                patch,
                filename,
            )

            summary = review.get("summary")

            if summary:
                all_summaries.append(
                    f"### {filename}\n{summary}"
                )

            issues = review.get("issues", [])

            for issue in issues:

                if not issue.get("file"):
                    issue["file"] = filename

                all_issues.append(issue)

        logger.info(
            "Completed AI review of %s files.",
            len(all_summaries),
        )

        # Post inline comments
        for issue in all_issues:

            file_path = issue.get("file")
            line = issue.get("line")
            comment = issue.get("comment")

            if not file_path or not line or not comment:
                logger.warning(
                    "Skipping invalid issue: %s",
                    issue,
                )
                continue

            try:

                github_service.create_inline_review_comment(
                    pull_number=pull_number,
                    file_path=file_path,
                    line=line,
                    comment=comment,
                )

                logger.info(
                    "Posted inline comment to %s:%s",
                    file_path,
                    line,
                )

            except Exception as exc:

                logger.exception(
                    "Failed to post inline comment for %s:%s. Error: %s",
                    file_path,
                    line,
                    exc,
                )

        summary_comment = "# 🤖 AI Code Review Report\n\n"

        if all_summaries:
            summary_comment += "\n\n".join(all_summaries)
        else:
            summary_comment += "No supported source code files were found to review."

        github_service.create_pull_request_comment(
            pull_number,
            summary_comment,
        )

        logger.info(
            "Completed AI review for PR #%s",
            pull_number,
        )

        return {
            "summary": summary_comment,
            "issues": all_issues,
        }


review_service = ReviewService()