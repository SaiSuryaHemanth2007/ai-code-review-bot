from pydantic import BaseModel


class ReviewComment(BaseModel):
    """
    Represents a single inline AI review comment.
    """

    path: str
    line: int
    severity: str
    comment: str