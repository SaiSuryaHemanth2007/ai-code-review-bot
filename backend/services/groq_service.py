"""
Groq AI service.

Handles communication with the Groq API.
"""

import json
from pathlib import Path

from groq import Groq

from backend.core.logger import logger
from backend.core.settings import settings


class GroqService:
    """Service for interacting with the Groq API."""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

        prompt_path = Path("backend/prompts/review_prompt.txt")
        self.review_prompt = prompt_path.read_text(encoding="utf-8")

    def review_code(self, code: str, language: str) -> dict:
        """
        Send code to Groq and return a parsed JSON review.
        """

        logger.info("Generating AI review using Groq...")

        prompt = f"""
{self.review_prompt}

IMPORTANT:

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
- Do NOT explain anything.
- Do NOT wrap JSON inside markdown.
- Do NOT use ```json.
- Return ONLY JSON.
- If no issues are found, return an empty issues array.

Language:
{language}

Code:
{code}
"""

        try:
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
            logger.info("Original AI Response:\n%s", content)

            cleaned = content

            # Remove Markdown code fences
            cleaned = cleaned.replace("```json", "")
            cleaned = cleaned.replace("```", "")
            cleaned = cleaned.strip()

            # Extract JSON object
            start = cleaned.find("{")
            end = cleaned.rfind("}")

            if start != -1 and end != -1:
                cleaned = cleaned[start:end + 1]

            logger.info("Cleaned AI Response:\n%s", cleaned)

            review = json.loads(cleaned)

            logger.info("Successfully parsed AI JSON.")

            return review

        except json.JSONDecodeError:
            logger.exception("Failed to parse AI JSON.")

            return {
                "summary": content,
                "issues": [],
            }

        except Exception:
            logger.exception("Groq request failed.")

            return {
                "summary": "Failed to generate AI review.",
                "issues": [],
            }


groq_service = GroqService()