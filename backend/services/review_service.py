from backend.core.logger import logger
from backend.services.github_service import github_service
from backend.services.groq_service import groq_service


class ReviewService:
    """Coordinates the AI review process."""

    def review(self, code: str, language: str):
        """Review a code snippet."""
        return groq_service.review_code(code, language)

    def review_pull_request(self, pull_number: int):
        """Review an entire GitHub pull request."""

        logger.info("Starting AI review for PR #%s", pull_number)

        files = github_service.get_pull_request_files(pull_number)

        combined_diff = ""

        for file in files:
            combined_diff += f"\n\nFILE: {file['filename']}\n"
            combined_diff += file.get("patch") or ""

        logger.info("Sending pull request diff to Groq...")

        review = groq_service.review_code(
            combined_diff,
            "GitHub Pull Request",
        )

        logger.info("AI review generated successfully.")

        # Post inline review comments
        for issue in review.get("issues", []):

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

        # Post summary comment
        github_service.create_pull_request_comment(
            pull_number,
            review.get(
                "summary",
                "AI review completed successfully.",
            ),
        )

        logger.info(
            "Completed AI review for PR #%s",
            pull_number,
        )

        return review


review_service = ReviewService()