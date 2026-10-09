from main import load_config


def test_global_keywords_merge():
    base, profile = load_config()

    assert "AI Engineer" in profile["linkedin"]["keywords"]
    assert "Software Developer" in profile["linkedin"]["keywords"]

    # ensure profile keywords were NOT kept
    assert isinstance(profile["linkedin"]["keywords"], list)
    assert len(profile["linkedin"]["keywords"]) > 0
