import json
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

    def review_code(self, code: str, language: str) -> dict:
        """Generate an AI code review in JSON format."""

        logger.info("Generating AI review using Groq...")

        prompt = f"""
{self.review_prompt}

Return ONLY valid JSON.

Expected format:

{{
  "summary": "Overall review summary",
  "issues": [
    {{
      "file": "",
      "line": 1,
      "severity": "LOW",
      "comment": ""
    }}
  ]
}}

Rules:
- Return valid JSON only.
- Do not wrap the JSON in markdown.
- Do not use ```json.
- If no issues are found, return an empty issues array.

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

        content = response.choices[0].message.content.strip()

        logger.info("Groq response received.")

        try:
            return json.loads(content)

        except json.JSONDecodeError:
            logger.exception("Groq returned invalid JSON.")

            return {
                "summary": content,
                "issues": [],
            }


groq_service = GroqService()