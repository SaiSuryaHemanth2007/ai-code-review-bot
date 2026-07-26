from typing import Dict


class QualityScore:

    @staticmethod
    def calculate(
        critical: int,
        high: int,
        medium: int,
        low: int,
    ) -> Dict:

        score = 100

        # Deduct points based on severity
        score -= critical * 25
        score -= high * 10
        score -= medium * 5
        score -= low * 2

        # Keep score between 0 and 100
        score = max(0, min(100, score))

        # Grade
        if score >= 90:
            grade = "A+"
            stars = "★★★★★"
        elif score >= 80:
            grade = "A"
            stars = "★★★★☆"
        elif score >= 70:
            grade = "B"
            stars = "★★★☆☆"
        elif score >= 60:
            grade = "C"
            stars = "★★☆☆☆"
        else:
            grade = "Needs Improvement"
            stars = "★☆☆☆☆"

        return {
            "score": score,
            "grade": grade,
            "stars": stars,
        }