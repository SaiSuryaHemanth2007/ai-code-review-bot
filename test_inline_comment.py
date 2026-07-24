from backend.services.github_service import github_service

github_service.create_inline_review_comment(
    pull_number=1,
    file_path="README.md",
    line=3,
    comment="✅ Test inline review comment from AI Code Review Bot",
)

print("Inline comment posted successfully!")