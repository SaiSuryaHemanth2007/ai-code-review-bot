from backend.schemas.review_comment import ReviewComment


def test_review_comment_schema():
    comment = ReviewComment(
        path="backend/main.py",
        line=10,
        severity="HIGH",
        comment="Potential security issue.",
    )

    assert comment.path == "backend/main.py"
    assert comment.line == 10
    assert comment.severity == "HIGH"
    assert comment.comment == "Potential security issue."