import pytest

from backend.services.github_event_service import (
    GitHubEventService,
)


@pytest.fixture
def service():
    return GitHubEventService()


# ---------------------------------------------------------
# should_review
# ---------------------------------------------------------

def test_should_review_opened_pull_request(service):
    payload = {
        "action": "opened",
    }

    assert service.should_review(
        "pull_request",
        payload,
    ) is True


def test_should_review_reopened_pull_request(service):
    payload = {
        "action": "reopened",
    }

    assert service.should_review(
        "pull_request",
        payload,
    ) is True


def test_should_review_synchronize_pull_request(service):
    payload = {
        "action": "synchronize",
    }

    assert service.should_review(
        "pull_request",
        payload,
    ) is True


def test_should_not_review_unsupported_pull_request_action(
    service,
):
    payload = {
        "action": "closed",
    }

    assert service.should_review(
        "pull_request",
        payload,
    ) is False


def test_should_not_review_non_pull_request_event(
    service,
):
    payload = {
        "action": "opened",
    }

    assert service.should_review(
        "push",
        payload,
    ) is False


def test_should_not_review_missing_action(service):
    payload = {}

    assert service.should_review(
        "pull_request",
        payload,
    ) is False


# ---------------------------------------------------------
# get_pull_request_number
# ---------------------------------------------------------

def test_get_pull_request_number_returns_number(service):
    payload = {
        "pull_request": {
            "number": 42,
        },
    }

    result = service.get_pull_request_number(
        payload
    )

    assert result == 42


def test_get_pull_request_number_rejects_missing_pull_request(
    service,
):
    payload = {}

    with pytest.raises(
        ValueError,
        match="Pull request data not found.",
    ):
        service.get_pull_request_number(
            payload
        )


def test_get_pull_request_number_rejects_missing_number(
    service,
):
    payload = {
        "pull_request": {
            "title": "Test PR",
        },
    }

    with pytest.raises(
        ValueError,
        match="Pull request number not found.",
    ):
        service.get_pull_request_number(
            payload
        )



# ---------------------------------------------------------
# get_repository
# ---------------------------------------------------------

def test_get_repository_returns_full_name(service):
    payload = {
        "repository": {
            "full_name": "owner/repository",
        },
    }

    result = service.get_repository(
        payload
    )

    assert result == "owner/repository"


def test_get_repository_rejects_missing_repository(
    service,
):
    payload = {}

    with pytest.raises(
        ValueError,
        match="Repository data not found.",
    ):
        service.get_repository(
            payload
        )


def test_get_repository_rejects_missing_full_name(
    service,
):
    payload = {
        "repository": {
            "name": "test-repo",
        },
    }

    with pytest.raises(
        ValueError,
        match="Repository full_name not found.",
    ):
        service.get_repository(
            payload
        )