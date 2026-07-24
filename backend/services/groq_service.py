"""
Groq AI service.

Handles communication with the Groq API.
"""

import json
from pathlib import Path

from groq import Groq

from backend.config.repository_context import REPOSITORY_CONTEXT
from backend.config.review_rules import REVIEW_RULES
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
        logger.info("Detected language: %s", language)

        enabled_rules = []

        for rule, enabled in REVIEW_RULES.items():
            if enabled:
                enabled_rules.append(
                    rule.replace("_", " ").title()
                )

        rules_text = "\n".join(
            f"- {rule}"
            for rule in enabled_rules
        )

        prompt = (
            self.review_prompt
            .replace("{language}", language)
            .replace("{rules}", rules_text)
            .replace(
                "{repository_context}",
                REPOSITORY_CONTEXT,
            )
            .replace("{code}", code)
        )

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

            cleaned = content.strip()

            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]

            if cleaned.startswith("```"):
                cleaned = cleaned[3:]

            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

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