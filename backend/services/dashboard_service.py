from backend.utils.history_db import history_db


class DashboardService:
    """Service for dashboard analytics."""

    def get_dashboard_summary(self):
        stats = history_db.get_statistics()
        reviews = history_db.get_all_reviews()

        total_files = sum(review["total_files"] for review in reviews)
        total_issues = sum(review["total_issues"] for review in reviews)

        repositories = len(set(review["repository"] for review in reviews))

        provider_usage = {}

        for review in reviews:
            provider = review["provider"]
            provider_usage[provider] = provider_usage.get(provider, 0) + 1

        return {
            "total_reviews": stats["total_reviews"],
            "average_quality_score": stats["average_score"],
            "total_files_reviewed": total_files,
            "total_issues_found": total_issues,
            "average_review_duration": stats["average_duration"],
            "repositories": repositories,
            "provider_usage": provider_usage,
        }

    def get_quality_history(self):
        reviews = history_db.get_all_reviews()
        reviews.reverse()

        return {
            "quality_scores": [
                review["quality_score"]
                for review in reviews
            ]
        }

    def get_review_trends(self):
        reviews = history_db.get_all_reviews()

        trends = {}

        for review in reviews:
            date = review["created_at"][:10]
            trends[date] = trends.get(date, 0) + 1

        return {
            "dates": list(trends.keys()),
            "review_counts": list(trends.values()),
        }

    def get_repository_statistics(self):
        reviews = history_db.get_all_reviews()

        repositories = {}

        for review in reviews:
            repo = review["repository"]

            if repo not in repositories:
                repositories[repo] = {
                    "reviews": 0,
                    "quality": 0,
                    "files": 0,
                    "issues": 0,
                }

            repositories[repo]["reviews"] += 1
            repositories[repo]["quality"] += review["quality_score"]
            repositories[repo]["files"] += review["total_files"]
            repositories[repo]["issues"] += review["total_issues"]

        result = []

        for repo, data in repositories.items():
            result.append({
                "repository": repo,
                "reviews": data["reviews"],
                "average_quality": round(
                    data["quality"] / data["reviews"], 2
                ),
                "files_reviewed": data["files"],
                "issues_found": data["issues"],
            })

        return {"repositories": result}

    def get_provider_statistics(self):
        reviews = history_db.get_all_reviews()

        providers = {}

        for review in reviews:
            provider = review["provider"]

            if provider not in providers:
                providers[provider] = {
                    "reviews": 0,
                    "quality": 0,
                    "duration": 0,
                }

            providers[provider]["reviews"] += 1
            providers[provider]["quality"] += review["quality_score"]
            providers[provider]["duration"] += review["review_duration"]

        result = {}

        for provider, data in providers.items():
            result[provider] = {
                "reviews": data["reviews"],
                "average_quality": round(
                    data["quality"] / data["reviews"], 2
                ),
                "average_duration": round(
                    data["duration"] / data["reviews"], 2
                ),
            }

        return {
            "providers": result
        }
    def get_leaderboard(self):
        """Return leaderboard statistics."""

        reviews = history_db.get_all_reviews()

        if not reviews:
            empty = {
                "repository": "",
                "pull_request": 0,
                "value": 0,
            }

            return {
                "highest_quality_review": empty,
                "fastest_review": empty,
                "largest_review": empty,
                "most_issues_found": empty,
            }

        highest_quality = max(
            reviews,
            key=lambda r: r["quality_score"]
        )

        fastest_review = min(
            reviews,
            key=lambda r: r["review_duration"]
        )

        largest_review = max(
            reviews,
            key=lambda r: r["total_files"]
        )

        most_issues = max(
            reviews,
            key=lambda r: r["total_issues"]
        )

        return {
            "highest_quality_review": {
                "repository": highest_quality["repository"],
                "pull_request": highest_quality["pull_request"],
                "value": highest_quality["quality_score"],
            },
            "fastest_review": {
                "repository": fastest_review["repository"],
                "pull_request": fastest_review["pull_request"],
                "value": fastest_review["review_duration"],
            },
            "largest_review": {
                "repository": largest_review["repository"],
                "pull_request": largest_review["pull_request"],
                "value": largest_review["total_files"],
            },
            "most_issues_found": {
                "repository": most_issues["repository"],
                "pull_request": most_issues["pull_request"],
                "value": most_issues["total_issues"],
             },
        }


dashboard_service = DashboardService()