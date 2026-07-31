from backend.services.github_service import github_service

github_service.create_pull_request_comment(
    1,
    "✅ Test comment from AI Code Review Bot"
)

print("Comment posted successfully!")