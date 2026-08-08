from unittest.mock import patch

from backend.services.groq_service import GroqService


def test_review_prompt_contains_sql_injection_safety_rules():
    with patch("backend.services.groq_service.Groq"):
        service = GroqService()

    prompt = service._build_prompt(
        """
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = ?"
    return query, (user_id,)
""",
        "Python",
    )

    assert (
        "Do NOT report SQL injection when user-controlled values "
        "are safely passed through parameterized queries"
        in prompt
    )

    assert (
        "Report SQL injection only when untrusted input is directly "
        "concatenated, interpolated, or formatted into an SQL statement "
        "without parameterization"
        in prompt
    )