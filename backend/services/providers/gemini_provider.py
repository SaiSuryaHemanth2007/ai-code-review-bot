"""
Gemini AI Provider.

Implements the BaseAIProvider interface.
"""

import json

from google import genai

from backend.core.logger import logger
from backend.core.settings import settings
from backend.services.providers.base_provider import (
    BaseAIProvider,
)


class GeminiProvider(BaseAIProvider):
    """
    Gemini implementation of BaseAIProvider.
    """

    def __init__(self):
        self.client = None

        if settings.GEMINI_API_KEY:
            self.client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

    @property
    def provider_name(self) -> str:
        return "Gemini"

    def review_code(
        self,
        code: str,
        language: str,
    ) -> dict:
        """
        Review source code using Gemini.
        """
        if self.client is None:
            return {
                "success": False,
                "error": "NOT_CONFIGURED",
                "summary": (
                    "Gemini API key is not configured."
                ),
                "issues": [],
            }

        logger.info(
            "Generating AI review using Gemini..."
        )

        logger.info(
            "Detected language: %s",
            language,
        )

        prompt = f"""
You are an expert software code reviewer.

Review the following {language} code.

Identify important:

- Bugs
- Security issues
- Performance problems
- Code quality issues
- Best-practice violations

Return ONLY valid JSON.

The JSON must follow this structure:

{{
    "summary": "Short summary of the code review.",
    "issues": [
        {{
            "file": null,
            "line": null,
            "severity": "LOW",
            "category": "Best Practices",
            "confidence": 60,
            "comment": "Description of the issue.",
            "suggestion": "How to fix the issue.",
            "occurrences": null,
            "files": null
        }}
    ]
}}

Severity must be one of:
CRITICAL, HIGH, MEDIUM, LOW.

Confidence must be an integer from 0 to 100.

If there are no issues, return an empty issues array.

Code to review:

```{language}
{code}

"""

        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
            )

            if response is None:
                logger.error(
                    "Gemini returned no response."
                )

                return {
                    "success": False,
                    "error": "EMPTY_RESPONSE",
                    "summary": (
                        "Gemini returned an empty response."
                    ),
                    "issues": [],
                }

            content = getattr(
                response,
                "text",
                None,
            )

            if not content:
                logger.error(
                    "Gemini response contained no text."
                )

                return {
                    "success": False,
                    "error": "EMPTY_RESPONSE",
                    "summary": (
                        "Gemini returned an empty response."
                    ),
                    "issues": [],
                }

            content = content.strip()

            logger.info(
                "Gemini response received."
            )

            logger.info(
                "Original Gemini Response:\n%s",
                content,
            )

            cleaned = content

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
                "Cleaned Gemini Response:\n%s",
                cleaned,
            )

            review_data = json.loads(cleaned)

            issues = review_data.get(
                "issues",
                [],
            )

            for issue in issues:

                if "confidence" not in issue:
                    severity = issue.get(
                        "severity",
                        "LOW",
                    ).upper()

                    confidence_map = {
                        "CRITICAL": 95,
                        "HIGH": 90,
                        "MEDIUM": 75,
                        "LOW": 60,
                    }

                    issue["confidence"] = (
                        confidence_map.get(
                            severity,
                            60,
                        )
                    )

                if "category" not in issue:
                    issue["category"] = (
                        "Best Practices"
                    )

            return {
                "success": True,
                "language": language,
                **review_data,
            }

        except json.JSONDecodeError:

            logger.exception(
                "Failed to parse Gemini response as JSON."
            )

            return {
                "success": False,
                "error": "INVALID_JSON",
                "summary": (
                    "Gemini returned invalid JSON."
                ),
                "issues": [],
            }

        except Exception:

            logger.exception(
                "Gemini request failed."
            )

            return {
                "success": False,
                "error": "GEMINI_ERROR",
                "summary": (
                    "Failed to generate AI review "
                    "using Gemini."
                ),
                "issues": [],
            }

    def health_check(self) -> bool:
        """
        Check whether Gemini is configured.
        """

        return bool(
            settings.GEMINI_API_KEY
        )


gemini_provider = GeminiProvider()
