from pydantic import BaseModel


class WebhookStatus(BaseModel):
    success: bool
    message: str
    job_id: str | None = None