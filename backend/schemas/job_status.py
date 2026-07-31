from typing import Optional

from pydantic import BaseModel, Field


class JobStatusResponse(BaseModel):
    """
    Represents the current status of a background review job.
    """

    job_id: str = Field(
        ...,
        description="Unique job identifier",
    )

    repository: str = Field(
        ...,
        description="GitHub repository name",
    )

    pull_request: int = Field(
        ...,
        description="Pull Request number",
    )

    status: str = Field(
        ...,
        description="Current job status",
        examples=["queued", "running", "completed", "failed"],
    )

    progress: int = Field(
        ...,
        ge=0,
        le=100,
        description="Progress percentage",
    )

    created_at: str

    started_at: Optional[str] = None

    completed_at: Optional[str] = None

    error: Optional[str] = None