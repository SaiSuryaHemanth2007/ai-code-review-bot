from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Request,
)

from backend.core.settings import settings
from backend.core.webhook_security import webhook_security
from backend.schemas.webhook_status import WebhookStatus
from backend.services.webhook_service import webhook_service

router = APIRouter()


@router.post(
    "/webhooks/github",
    response_model=WebhookStatus,
    summary="GitHub Webhook",
)
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Receive GitHub webhook events.
    """

    # Verify webhook signature only in production
    if not settings.DEBUG:
        await webhook_security.verify_signature(request)

    # Parse GitHub payload
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid or empty JSON payload.",
        )

    # Get GitHub event header
    event = request.headers.get(
        "X-GitHub-Event",
        "",
    )

    # Process webhook
    result = webhook_service.process_webhook(
        event=event,
        payload=payload,
        background_tasks=background_tasks,
    )

    return WebhookStatus(**result)