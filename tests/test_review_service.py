from backend.services.review_service import ReviewService


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