from typing import Any, Dict, Optional

from pydantic import BaseModel


class WebhookEvent(BaseModel):
    event: str
    action: str
    repository: Dict[str, Any]
    pull_request: Optional[Dict[str, Any]] = None