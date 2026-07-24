from backend.services.ai_service import ai_service
from backend.services.github_service import github_service


class ReviewService:
    """Coordinates the review process."""

    def review(self, code: str, language: str) -> str:
        return ai_service.review_code(code, language)

    def review_pull_request(self, pull_number: int) -> str:
        files = github_service.get_pull_request_files(pull_number)

        combined_diff = ""

        for file in files:
            combined_diff += f"\n\nFILE: {file['filename']}\n"
            combined_diff += file.get("patch") or ""

        review = ai_service.review_code(
            combined_diff,
            "GitHub Pull Request",
        )

        # Automatically post the AI review to GitHub
        github_service.create_pull_request_comment(
            pull_number,
            review,
        )

        return review


review_service = ReviewService()