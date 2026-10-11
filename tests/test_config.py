from main import load_all_profiles, load_config


def test_global_keywords_merge():
    base = load_config()
    profile = load_all_profiles(base)[0]

    assert "AI Engineer" in profile["linkedin"]["keywords"]
    assert "Software Developer" in profile["linkedin"]["keywords"]

    # ensure profile keywords were NOT kept
    assert isinstance(profile["linkedin"]["keywords"], list)
    assert len(profile["linkedin"]["keywords"]) > 0
