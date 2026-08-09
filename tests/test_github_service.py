from unittest.mock import MagicMock, patch

import pytest
from github.GithubException import GithubException

from backend.services.github_service import GitHubService


def test_init_with_github_token():
    with patch(
        "backend.services.github_service.settings.GITHUB_TOKEN",
        "test-token",
    ), patch(
        "backend.services.github_service.Auth.Token"
    ) as mock_auth, patch(
        "backend.services.github_service.Github"
    ) as mock_github:

        service = GitHubService()

    mock_auth.assert_called_once_with("test-token")
    mock_github.assert_called_once_with(
        auth=mock_auth.return_value
    )

    assert service.github == mock_github.return_value


def test_init_without_github_token():
    with patch(
        "backend.services.github_service.settings.GITHUB_TOKEN",
        "",
    ):

        service = GitHubService()

    assert service.github is None


def test_get_repository_returns_configured_repository():
    service = GitHubService()
    mock_github = MagicMock()

    service.github = mock_github

    with patch(
        "backend.services.github_service.settings.GITHUB_OWNER",
        "test-owner",
    ), patch(
        "backend.services.github_service.settings.GITHUB_REPOSITORY",
        "test-repo",
    ):

        result = service.get_repository()

    mock_github.get_repo.assert_called_once_with(
        "test-owner/test-repo"
    )

    assert result == mock_github.get_repo.return_value


def test_get_repository_raises_when_github_client_missing():
    service = GitHubService()
    service.github = None

    with pytest.raises(
        RuntimeError,
        match="GitHub client is not initialized.",
    ):
        service.get_repository()


def test_get_repository_info_returns_repository_information():
    service = GitHubService()

    mock_repo = MagicMock()

    mock_repo.name = "test-repo"
    mock_repo.owner.login = "test-owner"
    mock_repo.description = "Test repository"
    mock_repo.default_branch = "main"
    mock_repo.stargazers_count = 25
    mock_repo.get_pulls.return_value.totalCount = 3

    with patch.object(
        service,
        "get_repository",
        return_value=mock_repo,
    ):

        result = service.get_repository_info()

    assert result == {
        "name": "test-repo",
        "owner": "test-owner",
        "description": "Test repository",
        "default_branch": "main",
        "stars": 25,
        "open_pull_requests": 3,
    }

    mock_repo.get_pulls.assert_called_once_with(
        state="open"
    )


def test_get_repository_info_reraises_github_exception():
    service = GitHubService()

    error = GithubException(
        500,
        "GitHub API failure",
        None,
    )

    with patch.object(
        service,
        "get_repository",
        side_effect=error,
    ):

        with pytest.raises(GithubException):
            service.get_repository_info()


def test_get_pull_requests_returns_open_pull_requests():
    service = GitHubService()

    mock_repo = MagicMock()

    pr1 = MagicMock()
    pr1.number = 42
    pr1.title = "Add authentication"
    pr1.user.login = "developer"
    pr1.state = "open"
    pr1.created_at = "2026-08-01"

    pr2 = MagicMock()
    pr2.number = 43
    pr2.title = "Improve caching"
    pr2.user.login = "developer2"
    pr2.state = "open"
    pr2.created_at = "2026-08-02"

    mock_repo.get_pulls.return_value = [
        pr1,
        pr2,
    ]

    with patch.object(
        service,
        "get_repository",
        return_value=mock_repo,
    ):

        result = service.get_pull_requests()

    assert result == [
        {
            "number": 42,
            "title": "Add authentication",
            "author": "developer",
            "state": "open",
            "created_at": "2026-08-01",
        },
        {
            "number": 43,
            "title": "Improve caching",
            "author": "developer2",
            "state": "open",
            "created_at": "2026-08-02",
        },
    ]

    mock_repo.get_pulls.assert_called_once_with(
        state="open"
    )


def test_get_pull_requests_reraises_github_exception():
    service = GitHubService()

    error = GithubException(
        500,
        "GitHub API failure",
        None,
    )

    with patch.object(
        service,
        "get_repository",
        side_effect=error,
    ):

        with pytest.raises(GithubException):
            service.get_pull_requests()


def test_get_pull_request_files_returns_changed_files():
    service = GitHubService()

    mock_repo = MagicMock()
    mock_pull = MagicMock()

    mock_file = MagicMock()

    mock_file.filename = "backend/main.py"
    mock_file.status = "modified"
    mock_file.additions = 10
    mock_file.deletions = 2
    mock_file.changes = 12
    mock_file.patch = "@@ -1,5 +1,13 @@"
    mock_file.blob_url = "https://github.com/test/blob/main/backend/main.py"
    mock_file.raw_url = "https://github.com/test/raw/main/backend/main.py"
    mock_file.contents_url = "https://api.github.com/test"

    mock_pull.get_files.return_value = [
        mock_file
    ]

    mock_repo.get_pull.return_value = mock_pull

    with patch.object(
        service,
        "get_repository",
        return_value=mock_repo,
    ):

        result = service.get_pull_request_files(42)

    assert result == [
        {
            "filename": "backend/main.py",
            "status": "modified",
            "additions": 10,
            "deletions": 2,
            "changes": 12,
            "patch": "@@ -1,5 +1,13 @@",
            "blob_url": "https://github.com/test/blob/main/backend/main.py",
            "raw_url": "https://github.com/test/raw/main/backend/main.py",
            "contents_url": "https://api.github.com/test",
        }
    ]

    mock_repo.get_pull.assert_called_once_with(42)
    mock_pull.get_files.assert_called_once()


def test_get_pull_request_files_reraises_github_exception():
    service = GitHubService()

    error = GithubException(
        500,
        "GitHub API failure",
        None,
    )

    with patch.object(
        service,
        "get_repository",
        side_effect=error,
    ):

        with pytest.raises(GithubException):
            service.get_pull_request_files(42)


def test_upsert_pull_request_comment_updates_existing_ai_comment():
    service = GitHubService()

    mock_repo = MagicMock()
    mock_pull = MagicMock()
    existing_comment = MagicMock()

    existing_comment.body = (
        f"{service.AI_REVIEW_HEADER}\nOld review"
    )
    existing_comment.id = 123

    mock_pull.get_issue_comments.return_value = [
        existing_comment
    ]

    mock_repo.get_pull.return_value = mock_pull

    with patch.object(
        service,
        "get_repository",
        return_value=mock_repo,
    ):

        result = service.upsert_pull_request_comment(
            42,
            "New review",
        )

    assert result is None

    mock_repo.get_pull.assert_called_once_with(42)
    existing_comment.edit.assert_called_once_with(
        "New review"
    )

    mock_pull.create_issue_comment.assert_not_called()


def test_upsert_pull_request_comment_creates_new_comment():
    service = GitHubService()

    mock_repo = MagicMock()
    mock_pull = MagicMock()

    existing_comment = MagicMock()
    existing_comment.body = "Some unrelated comment"

    created_comment = MagicMock()
    created_comment.id = 456

    mock_pull.get_issue_comments.return_value = [
        existing_comment
    ]
    mock_pull.create_issue_comment.return_value = (
        created_comment
    )

    mock_repo.get_pull.return_value = mock_pull

    with patch.object(
        service,
        "get_repository",
        return_value=mock_repo,
    ):

        result = service.upsert_pull_request_comment(
            42,
            "New review",
        )

    assert result is None

    mock_pull.create_issue_comment.assert_called_once_with(
        "New review"
    )

    existing_comment.edit.assert_not_called()


def test_upsert_pull_request_comment_reraises_github_exception():
    service = GitHubService()

    error = GithubException(
        500,
        "GitHub API failure",
        None,
    )

    with patch.object(
        service,
        "get_repository",
        side_effect=error,
    ):

        with pytest.raises(GithubException):
            service.upsert_pull_request_comment(
                42,
                "Review",
            )


def test_create_inline_review_comment_posts_comment():
    service = GitHubService()

    mock_repo = MagicMock()
    mock_pull = MagicMock()

    commit1 = MagicMock()
    commit2 = MagicMock()

    review_comment = MagicMock()
    review_comment.id = 999

    mock_pull.get_commits.return_value = [
        commit1,
        commit2,
    ]

    mock_pull.create_review_comment.return_value = (
        review_comment
    )

    mock_repo.get_pull.return_value = mock_pull

    with patch.object(
        service,
        "get_repository",
        return_value=mock_repo,
    ):

        result = service.create_inline_review_comment(
            pull_number=42,
            file_path="backend/main.py",
            line=15,
            comment="Potential issue here.",
        )

    assert result is None

    mock_repo.get_pull.assert_called_once_with(42)

    mock_pull.create_review_comment.assert_called_once_with(
        body="Potential issue here.",
        commit=commit2,
        path="backend/main.py",
        line=15,
        side="RIGHT",
    )


def test_create_inline_review_comment_rejects_missing_commits():
    service = GitHubService()

    mock_repo = MagicMock()
    mock_pull = MagicMock()

    mock_pull.get_commits.return_value = []

    mock_repo.get_pull.return_value = mock_pull

    with patch.object(
        service,
        "get_repository",
        return_value=mock_repo,
    ):

        with pytest.raises(
            RuntimeError,
            match="No commits found for pull request.",
        ):
            service.create_inline_review_comment(
                pull_number=42,
                file_path="backend/main.py",
                line=15,
                comment="Potential issue here.",
            )

    mock_pull.create_review_comment.assert_not_called()


def test_create_inline_review_comment_reraises_github_exception():
    service = GitHubService()

    error = GithubException(
        500,
        "GitHub API failure",
        None,
    )

    with patch.object(
        service,
        "get_repository",
        side_effect=error,
    ):

        with pytest.raises(GithubException):
            service.create_inline_review_comment(
                pull_number=42,
                file_path="backend/main.py",
                line=15,
                comment="Review",
            )