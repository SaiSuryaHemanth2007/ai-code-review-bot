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

        return ai_service.review_code(
            combined_diff,
            "GitHub Pull Request",
        )


review_service = ReviewService()