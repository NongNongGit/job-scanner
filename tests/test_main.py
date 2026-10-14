import main


def test_retry_returns_on_successful_attempt(monkeypatch):
    attempts = []

    def succeed_on_third_attempt():
        attempts.append(None)
        if len(attempts) < 3:
            raise RuntimeError("temporary failure")
        return ["result"]

    sleeps = []
    monkeypatch.setattr("time.sleep", sleeps.append)

    assert main.retry(succeed_on_third_attempt, 3, 2) == ["result"]
    assert len(attempts) == 3
    assert sleeps == [2, 2]


def test_retry_returns_empty_list_after_all_attempts_fail(monkeypatch):
    attempts = []
    sleeps = []

    def always_fail():
        attempts.append(None)
        raise RuntimeError("persistent failure")

    monkeypatch.setattr("time.sleep", sleeps.append)

    assert main.retry(always_fail, 2, 1) == []
    assert len(attempts) == 2
    assert sleeps == [1]
