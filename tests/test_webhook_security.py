import hashlib
import hmac
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from backend.core.webhook_security import WebhookSecurity


@pytest.mark.anyio
async def test_verify_signature_returns_true_for_valid_signature():
    secret = "test-secret"
    payload = b'{"action":"opened"}'

    expected_signature = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
    )

    request = MagicMock()

    request.headers.get.return_value = expected_signature
    request.body = AsyncMock(return_value=payload)

    with patch(
        "backend.core.webhook_security.settings.GITHUB_WEBHOOK_SECRET",
        secret,
    ):
        result = await WebhookSecurity.verify_signature(
            request
        )

    assert result is True

    request.headers.get.assert_called_once_with(
        "X-Hub-Signature-256"
    )
    request.body.assert_awaited_once()


@pytest.mark.anyio
async def test_verify_signature_rejects_invalid_signature():
    secret = "test-secret"
    payload = b'{"action":"opened"}'

    request = MagicMock()

    request.headers.get.return_value = (
        "sha256=invalid-signature"
    )
    request.body = AsyncMock(return_value=payload)

    with patch(
        "backend.core.webhook_security.settings.GITHUB_WEBHOOK_SECRET",
        secret,
    ):
        with pytest.raises(
            HTTPException,
            match="Invalid GitHub webhook signature.",
        ) as exc_info:

            await WebhookSecurity.verify_signature(
                request
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == (
        "Invalid GitHub webhook signature."
    )


@pytest.mark.anyio
async def test_verify_signature_rejects_missing_signature():
    request = MagicMock()

    request.headers.get.return_value = None

    with patch(
        "backend.core.webhook_security.settings.GITHUB_WEBHOOK_SECRET",
        "test-secret",
    ):
        with pytest.raises(
            HTTPException,
            match="Missing GitHub webhook signature.",
        ) as exc_info:

            await WebhookSecurity.verify_signature(
                request
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == (
        "Missing GitHub webhook signature."
    )


@pytest.mark.anyio
async def test_verify_signature_rejects_missing_secret():
    request = MagicMock()

    with patch(
        "backend.core.webhook_security.settings.GITHUB_WEBHOOK_SECRET",
        "",
    ):
        with pytest.raises(
            RuntimeError,
            match="GITHUB_WEBHOOK_SECRET is not configured.",
        ):
            await WebhookSecurity.verify_signature(
                request
            )

    request.headers.get.assert_not_called()


@pytest.mark.anyio
async def test_verify_signature_uses_request_body():
    secret = "test-secret"

    payload = b'{"repository":"test/repo"}'

    expected_signature = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
    )

    request = MagicMock()

    request.headers.get.return_value = expected_signature
    request.body = AsyncMock(return_value=payload)

    with patch(
        "backend.core.webhook_security.settings.GITHUB_WEBHOOK_SECRET",
        secret,
    ):
        result = await WebhookSecurity.verify_signature(
            request
        )

    assert result is True
    request.body.assert_awaited_once()