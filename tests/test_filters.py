from filters import apply_filters


def test_filter_salary():
    profile = {"filters": {"min_salary": 80000, "remote_only": False}}

    job = {"salary": 90000}
    assert apply_filters(job, profile) is True

    job = {"salary": 10000}
    assert apply_filters(job, profile) is False


def test_filter_remote():
    profile = {"filters": {"min_salary": 0, "remote_only": True}}

    job = {"remote": True}
    assert apply_filters(job, profile) is True

    job = {"remote": False}
    assert apply_filters(job, profile) is False
