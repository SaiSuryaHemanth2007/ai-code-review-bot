"""
Utilities for parsing AI review responses.
"""

import json
from typing import List

from backend.schemas.review_comment import ReviewComment


class ReviewParser:
    """
    Parses the AI JSON response into ReviewComment objects.
    """

    @staticmethod
    def parse(response: str, file_path: str) -> List[ReviewComment]:
        """
        Parse AI response into ReviewComment objects.
        """

        try:
            data = json.loads(response)

            comments = []

            for item in data:
                comments.append(
                    ReviewComment(
                        path=file_path,
                        line=item["line"],
                        severity=item["severity"],
                        comment=item["comment"],
                    )
                )

            return comments

        except Exception:
            return []


review_parser = ReviewParser()