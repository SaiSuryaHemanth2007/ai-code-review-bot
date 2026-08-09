from backend.utils.quality_score import QualityScore


def test_calculate_returns_a_plus_grade():
    result = QualityScore.calculate(
        critical=0,
        high=0,
        medium=0,
        low=0,
    )

    assert result["score"] == 100
    assert result["grade"] == "A+"
    assert result["stars"] == "★★★★★"


def test_calculate_returns_a_grade():
    result = QualityScore.calculate(
        critical=0,
        high=2,
        medium=0,
        low=0,
    )

    assert result["score"] == 80
    assert result["grade"] == "A"
    assert result["stars"] == "★★★★☆"


def test_calculate_returns_b_grade():
    result = QualityScore.calculate(
        critical=0,
        high=0,
        medium=6,
        low=0,
    )

    assert result["score"] == 70
    assert result["grade"] == "B"
    assert result["stars"] == "★★★☆☆"


def test_calculate_returns_c_grade():
    result = QualityScore.calculate(
        critical=0,
        high=0,
        medium=8,
        low=0,
    )

    assert result["score"] == 60
    assert result["grade"] == "C"
    assert result["stars"] == "★★☆☆☆"


def test_calculate_returns_needs_improvement():
    result = QualityScore.calculate(
        critical=5,
        high=0,
        medium=0,
        low=0,
    )

    assert result["score"] == 0
    assert result["grade"] == "Needs Improvement"
    assert result["stars"] == "★☆☆☆☆"