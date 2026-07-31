from fastapi import APIRouter, HTTPException

from backend.services.history_service import history_service

router = APIRouter(
    prefix="/history",
    tags=["Review History"],
)


@router.get("")
def get_all_reviews():
    """Get all saved reviews."""
    return history_service.get_all_reviews()


@router.get("/{review_id}")
def get_review(review_id: int):
    """Get a review by its ID."""
    review = history_service.get_review(review_id)

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found",
        )

    return review


@router.delete("/{review_id}")
def delete_review(review_id: int):
    """Delete a review."""
    deleted = history_service.delete_review(review_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Review not found",
        )

    return {
        "message": "Review deleted successfully"
    }


@router.get("/statistics")
def get_statistics():
    """Get review statistics."""
    return history_service.get_statistics()