import hashlib
import hmac

from fastapi import HTTPException, Request

from backend.core.settings import settings


class WebhookSecurity:
    """
    Handles GitHub webhook signature verification.
    """

    @staticmethod
    async def verify_signature(request: Request) -> bool:
        signature = request.headers.get("X-Hub-Signature-256")

        if signature is None:
            raise HTTPException(
                status_code=401,
                detail="Missing GitHub webhook signature.",
            )

        payload = await request.body()

        expected_signature = (
            "sha256="
            + hmac.new(
                settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
                payload,
                hashlib.sha256,
            ).hexdigest()
        )

        if not hmac.compare_digest(
            signature,
            expected_signature,
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid GitHub webhook signature.",
            )

        return True


webhook_security = WebhookSecurity()