from unittest.mock import patch

from backend.services.review_service import ReviewService


def test_review_file_calls_ai_on_cache_miss():
    service = ReviewService()

    review = {
        "success": True,
        "summary": "Review completed.",
        "issues": [],
    }

    with patch(
        "backend.services.review_service.get_cached_review",
        return_value=None,
    ), patch(
        "backend.services.review_service.ai_service.review_code",
        return_value=review,
    ) as mock_review, patch(
        "backend.services.review_service.store_review",
    ) as mock_store:

        result = service.review_file(
            "main.py",
            "print('hello')",
            "Python",
        )

    mock_review.assert_called_once_with(
        "print('hello')",
        "Python",
    )

    mock_store.assert_called_once()

    assert result == {
        "filename": "main.py",
        "review": review,
    }


def test_review_file_uses_cached_review_without_ai_call():
    service = ReviewService()

    review = {
        "success": True,
        "summary": "Cached review.",
        "issues": [],
    }

    with patch(
        "backend.services.review_service.get_cached_review",
        return_value=review,
    ), patch(
        "backend.services.review_service.ai_service.review_code",
    ) as mock_review, patch(
        "backend.services.review_service.store_review",
    ) as mock_store:

        result = service.review_file(
            "main.py",
            "print('hello')",
            "Python",
        )

    mock_review.assert_not_called()
    mock_store.assert_not_called()

    assert result == {
        "filename": "main.py",
        "review": review,
    }

def test_filters_builtin_sum_function_false_positive():
    service = ReviewService()

    issue = {
        "category": "Performance",
        "comment": "This function could be simplified using the built-in sum function.",
    }

    assert service._is_false_positive_issue(issue) is True


def test_filters_timing_attack_false_positive():
    service = ReviewService()

    issue = {
        "category": "Security",
        "comment": "The password comparison is vulnerable to timing attacks.",
    }

    assert service._is_false_positive_issue(issue) is True


def test_filters_small_helper_duplication_false_positive():
    service = ReviewService()

    issue = {
        "category": "Maintainability",
        "comment": (
            "The find_user, find_admin, find_moderator, and "
            "find_reviewer functions contain duplicated logic."
        ),
    }

    assert service._is_false_positive_issue(issue) is True

def test_filters_calculate_average_sum_suggestion_false_positive():
    service = ReviewService()

    issue = {
        "category": "Performance",
        "comment": (
            "The calculate_average function can be simplified "
            "using the built-in sum function."
        ),
    }

    assert service._is_false_positive_issue(issue) is True


def test_filters_get_delete_search_helper_duplication_false_positive():
    service = ReviewService()

    issue = {
        "category": "Maintainability",
        "comment": (
            "The get_user, delete_user, and search_user functions "
            "have similar structures and could be refactored "
            "for better maintainability."
        ),
    }

    assert service._is_false_positive_issue(issue) is True

def test_review_pull_request_skips_unsupported_files():
    service = ReviewService()

    files = [
        {
            "filename": "main.py",
            "patch": "@@ -1,1 +1,1 @@\n-print('old')\n+print('new')",
        },
        {
            "filename": "README.txt",
            "patch": "@@ -1,1 +1,1 @@\n-old\n+new",
        },
    ]

    review = {
        "success": True,
        "summary": "Review completed.",
        "issues": [],
    }

    with patch(
        "backend.services.review_service.github_service.get_pull_request_files",
        return_value=files,
    ), patch(
        "backend.services.review_service.get_cached_review",
        return_value=None,
    ), patch(
        "backend.services.review_service.ai_service.review_code",
        return_value=review,
    ) as mock_review, patch(
        "backend.services.review_service.store_review",
    ):

        result = service.review_pull_request(1)

    mock_review.assert_called_once_with(
        "@@ -1,1 +1,1 @@\n-print('old')\n+print('new')",
        "Python",
    )

    assert result["statistics"]["files_reviewed"] == 1

def test_review_pull_request_skips_files_without_patch():
    service = ReviewService()

    files = [
        {
            "filename": "main.py",
            "patch": "@@ -1,1 +1,1 @@\n-print('old')\n+print('new')",
        },
        {
            "filename": "config.py",
            "patch": None,
        },
    ]

    review = {
        "success": True,
        "summary": "Review completed.",
        "issues": [],
    }

    with patch(
        "backend.services.review_service.github_service.get_pull_request_files",
        return_value=files,
    ), patch(
        "backend.services.review_service.get_cached_review",
        return_value=None,
    ), patch(
        "backend.services.review_service.ai_service.review_code",
        return_value=review,
    ) as mock_review, patch(
        "backend.services.review_service.store_review",
    ):

        result = service.review_pull_request(1)

    mock_review.assert_called_once_with(
        "@@ -1,1 +1,1 @@\n-print('old')\n+print('new')",
        "Python",
    )

    assert result["statistics"]["files_reviewed"] == 1

def test_review_pull_request_skips_ignored_files():
    service = ReviewService()

    files = [
        {
            "filename": "main.py",
            "patch": "@@ -1,1 +1,1 @@\n-print('old')\n+print('new')",
        },
        {
            "filename": "__pycache__/cache.py",
            "patch": "@@ -1,1 +1,1 @@\n-old\n+new",
        },
    ]

    review = {
        "success": True,
        "summary": "Review completed.",
        "issues": [],
    }

    with patch(
        "backend.services.review_service.github_service.get_pull_request_files",
        return_value=files,
    ), patch(
        "backend.services.review_service.get_cached_review",
        return_value=None,
    ), patch(
        "backend.services.review_service.ai_service.review_code",
        return_value=review,
    ) as mock_review, patch(
        "backend.services.review_service.store_review",
    ):

        result = service.review_pull_request(1)

    mock_review.assert_called_once_with(
        "@@ -1,1 +1,1 @@\n-print('old')\n+print('new')",
        "Python",
    )

    assert result["statistics"]["files_reviewed"] == 1

def test_review_pull_request_reviews_multiple_supported_files():
    service = ReviewService()

    files = [
        {
            "filename": "main.py",
            "patch": "@@ -1,1 +1,1 @@\n-print('old')\n+print('new')",
        },
        {
            "filename": "app.js",
            "patch": "@@ -1,1 +1,1 @@\n-console.log('old')\n+console.log('new')",
        },
    ]

    review = {
        "success": True,
        "provider": "Groq",
        "summary": "Review completed.",
        "issues": [],
    }

    with patch(
        "backend.services.review_service.github_service.get_pull_request_files",
        return_value=files,
    ), patch(
        "backend.services.review_service.get_cached_review",
        return_value=None,
    ), patch(
        "backend.services.review_service.ai_service.review_code",
        return_value=review,
    ) as mock_review, patch(
        "backend.services.review_service.store_review",
    ):

        result = service.review_pull_request(1)

    assert mock_review.call_count == 2

    mock_review.assert_any_call(
        "@@ -1,1 +1,1 @@\n-print('old')\n+print('new')",
        "Python",
    )

    mock_review.assert_any_call(
        "@@ -1,1 +1,1 @@\n-console.log('old')\n+console.log('new')",
        "JavaScript",
    )

    assert result["statistics"]["files_reviewed"] == 2

def test_review_pull_request_counts_ai_failures():
    service = ReviewService()

    files = [
        {
            "filename": "main.py",
            "patch": "@@ -1,1 +1,1 @@\n-print('old')\n+print('new')",
        },
    ]

    failed_review = {
        "success": False,
        "provider": "Groq",
        "error": "RATE_LIMIT",
        "summary": "AI review failed.",
        "issues": [],
    }

    with patch(
        "backend.services.review_service.github_service.get_pull_request_files",
        return_value=files,
    ), patch(
        "backend.services.review_service.get_cached_review",
        return_value=None,
    ), patch(
        "backend.services.review_service.ai_service.review_code",
        return_value=failed_review,
    ), patch(
        "backend.services.review_service.store_review",
    ):

        result = service.review_pull_request(1)

    assert result["statistics"]["ai_failures"] == 1
    assert result["statistics"]["files_reviewed"] == 1

def test_review_pull_request_processes_ai_issues_and_calculates_quality():
    service = ReviewService()

    files = [
        {
            "filename": "main.py",
            "patch": "@@ -1,2 +1,2 @@\n-print('old')\n+password = input('Password: ')\n+print(password)",
        },
    ]

    review = {
        "success": True,
        "provider": "Groq",
        "summary": "A security issue was identified.",
        "issues": [
            {
                "file": "main.py",
                "line": 2,
                "severity": "HIGH",
                "category": "Security",
                "confidence": 90,
                "comment": "Sensitive password input is exposed.",
                "suggestion": "Avoid exposing sensitive credentials.",
                "occurrences": 1,
                "files": ["main.py"],
            }
        ],
    }

    with patch(
        "backend.services.review_service.github_service.get_pull_request_files",
        return_value=files,
    ), patch(
        "backend.services.review_service.get_cached_review",
        return_value=None,
    ), patch(
        "backend.services.review_service.ai_service.review_code",
        return_value=review,
    ), patch(
        "backend.services.review_service.store_review",
    ), patch(
        "backend.services.review_service.github_service.create_inline_review_comment",
    ) as mock_inline_comment, patch(
        "backend.services.review_service.github_service.upsert_pull_request_comment",
    ) as mock_pr_comment, patch(
        "backend.services.review_service.history_service.save_review",
        return_value=1,
    ):

        result = service.review_pull_request(1)

    assert result["statistics"]["files_reviewed"] == 1
    assert result["statistics"]["total_issues"] == 1

    assert result["statistics"]["high"] == 1
    assert result["statistics"]["critical"] == 0
    assert result["statistics"]["medium"] == 0
    assert result["statistics"]["low"] == 0

    assert result["quality"]["score"] < 100
    assert "grade" in result["quality"]
    assert "stars" in result["quality"]

    assert len(result["issues"]) == 1

    issue = result["issues"][0]

    assert issue["file"] == "main.py"
    assert issue["severity"] == "HIGH"
    assert issue["category"] == "Security"
    assert issue["confidence"] == 90

    assert mock_inline_comment.called
    mock_pr_comment.assert_called_once()

def test_review_pull_request_counts_all_severity_levels():
    service = ReviewService()

    files = [
        {
            "filename": "main.py",
            "patch": (
                "@@ -1,4 +1,4 @@\n"
                "-old\n"
                "+critical_change\n"
            ),
        },
    ]

    review = {
        "success": True,
        "provider": "Groq",
        "summary": "Multiple issues found.",
        "issues": [
            {
                "file": "main.py",
                "line": 1,
                "severity": "CRITICAL",
                "category": "Security",
                "confidence": 95,
                "comment": "Critical security issue.",
                "suggestion": "Fix immediately.",
            },
            {
                "file": "main.py",
                "line": 2,
                "severity": "HIGH",
                "category": "Security",
                "confidence": 90,
                "comment": "High severity issue.",
                "suggestion": "Fix this issue.",
            },
            {
                "file": "main.py",
                "line": 3,
                "severity": "MEDIUM",
                "category": "Performance",
                "confidence": 75,
                "comment": "Performance issue.",
                "suggestion": "Optimize this code.",
            },
            {
                "file": "main.py",
                "line": 4,
                "severity": "LOW",
                "category": "Style",
                "confidence": 60,
                "comment": "Minor style issue.",
                "suggestion": "Improve readability.",
            },
        ],
    }

    with patch(
        "backend.services.review_service.github_service.get_pull_request_files",
        return_value=files,
    ), patch(
        "backend.services.review_service.get_cached_review",
        return_value=None,
    ), patch(
        "backend.services.review_service.ai_service.review_code",
        return_value=review,
    ), patch(
        "backend.services.review_service.store_review",
    ), patch(
        "backend.services.review_service.github_service.create_inline_review_comment",
    ), patch(
        "backend.services.review_service.github_service.upsert_pull_request_comment",
    ), patch(
        "backend.services.review_service.history_service.save_review",
        return_value=1,
    ):

        result = service.review_pull_request(1)

    statistics = result["statistics"]

    assert statistics["critical"] == 1
    assert statistics["high"] == 1
    assert statistics["medium"] == 1
    assert statistics["low"] == 1

    assert statistics["total_issues"] == 4
    assert statistics["files_reviewed"] == 1

    assert result["quality"]["score"] < 100
    assert len(result["issues"]) == 4