from backend.schemas.webhook_event import WebhookEvent


def test_webhook_event_schema():
    event = WebhookEvent(
        event="pull_request",
        action="opened",
        repository={
            "full_name": "example/repository",
        },
    )

    assert event.event == "pull_request"
    assert event.action == "opened"
    assert event.repository["full_name"] == "example/repository"
    assert event.pull_request is None


def test_webhook_event_with_pull_request():
    event = WebhookEvent(
        event="pull_request",
        action="opened",
        repository={
            "full_name": "example/repository",
        },
        pull_request={
            "number": 42,
        },
    )

    assert event.pull_request["number"] == 42