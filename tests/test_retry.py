from backend.utils.retry import retry


def test_retry_success():

    calls = {"count": 0}

    @retry(retries=3, delay=0)
    def sample():

        calls["count"] += 1

        if calls["count"] < 2:
            raise Exception("Temporary failure")

        return "success"

    assert sample() == "success"
    assert calls["count"] == 2


def test_retry_failure():

    @retry(retries=2, delay=0)
    def always_fail():
        raise Exception("Always fails")

    try:
        always_fail()
        assert False
    except Exception as exc:
        assert str(exc) == "Always fails"