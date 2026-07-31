from pydantic import BaseModel, Field


class JobResponse(BaseModel):
    """
    Response returned after creating a background review job.
    """

    message: str = Field(
        ...,
        description="Job creation message",
        examples=["Review job created successfully."],
    )

    job_id: str = Field(
        ...,
        description="Unique background job identifier",
    )

    status: str = Field(
        ...,
        description="Initial job status",
        examples=["queued"],
    )