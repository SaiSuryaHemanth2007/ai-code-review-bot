from backend.services.groq_service import groq_service

review = groq_service.review_code(
    """
def add(a,b):
    return a+b
""",
    "Python",
)

print(review)