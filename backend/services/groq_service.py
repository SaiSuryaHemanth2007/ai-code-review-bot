from pathlib import Path

from groq import Groq

from backend.core.logger import logger
from backend.core.settings import settings


class GroqService:
    """Service for communicating with the Groq API."""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

        prompt_path = Path("backend/prompts/review_prompt.txt")
        self.review_prompt = prompt_path.read_text(encoding="utf-8")

    def review_code(self, code: str, language: str) -> str:
        logger.info("Generating AI review using Groq...")

        prompt = f"""
{self.review_prompt}

Language:
{language}

Code:

{code}
"""

        response = self.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content


groq_service = GroqService()