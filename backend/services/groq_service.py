"""
Groq AI service.

Handles communication with the Groq API.
"""

import json
import time
from pathlib import Path

from groq import Groq

from backend.config.repository_context import REPOSITORY_CONTEXT
from backend.config.review_rules import REVIEW_RULES
from backend.core.logger import logger
from backend.core.settings import settings
# Cache is handled by review_service.py

MAX_RETRIES = 3


class GroqService:
    """Service for interacting with the Groq API."""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

        prompt_path = Path("backend/prompts/review_prompt.txt")
        self.review_prompt = prompt_path.read_text(
            encoding="utf-8"
        )

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

        response = None

        for attempt in range(MAX_RETRIES):

            try:

                logger.info(
                    "Groq request attempt %s/%s",
                    attempt + 1,
                    MAX_RETRIES,
                )

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

                logger.info(
                    "Groq request succeeded."
                )

                break

            except Exception as e:

                logger.exception(
                    "Groq request failed : %s",
                    str(e),
                )

                if attempt == MAX_RETRIES - 1:

                    return {
                        "summary": "Failed to generate AI review after multiple attempts.",
                        "issues": [],
                    }

                wait_time = 2 ** attempt

                logger.info(
                    "Retrying in %s seconds...",
                    wait_time,
                )

                time.sleep(wait_time)

        try:

            content = response.choices[0].message.content.strip()

            logger.info("Groq response received.")
            logger.info(
                "Original AI Response:\n%s",
                content,
            )

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

            logger.info(
                "Cleaned AI Response:\n%s",
                cleaned,
            )

            review = json.loads(cleaned)

            # Ensure every issue has confidence and category
            for issue in review.get("issues", []):

                if "confidence" not in issue:
                    severity = issue.get("severity", "LOW").upper()

                    if severity == "CRITICAL":
                        issue["confidence"] = 95
                    elif severity == "HIGH":
                        issue["confidence"] = 90
                    elif severity == "MEDIUM":
                        issue["confidence"] = 75
                    else:
                        issue["confidence"] = 60

                if "category" not in issue:
                    issue["category"] = "Best Practices"


            logger.info(
                "Successfully parsed AI JSON."
            )

            return review

        except json.JSONDecodeError:

            logger.exception(
                "Failed to parse AI JSON."
            )

            return {
                "summary": content,
                "issues": [],
            }

        except Exception:

            logger.exception(
                "Unexpected error processing AI response."
            )

            return {
                "summary": "Failed to generate AI review.",
                "issues": [],
            }


groq_service = GroqService()