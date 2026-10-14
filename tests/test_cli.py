import json

import pytest

import main


def test_cli_passes_external_paths_to_scanner(monkeypatch):
    calls = []
    monkeypatch.setattr(
        main, "main", lambda **paths: calls.append(paths)
    )

    main.cli(
        [
            "--config",
            "/settings/scanner.json",
            "--cv",
            "/private/cv.txt",
            "--output",
            "/results/jobs.json",
        ]
    )

    assert calls == [
        {
            "config_path": "/settings/scanner.json",
            "cv_path": "/private/cv.txt",
            "output_path": "/results/jobs.json",
        }
    ]


def test_cli_defaults_preserve_checkout_paths(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "main", lambda **paths: calls.append(paths))

    main.cli([])

    assert calls == [
        {
            "config_path": "config.json",
            "cv_path": "cv.txt",
            "output_path": "jobs.json",
        }
    ]


def test_cli_help_is_available(capsys):
    with pytest.raises(SystemExit) as error:
        main.cli(["--help"])

    assert error.value.code == 0
    help_text = capsys.readouterr().out
    assert "--config" in help_text
    assert "--cv" in help_text
    assert "--output" in help_text


@pytest.mark.parametrize(
    ("profile_reference", "profile_location"),
    [
        ("north.json", "profiles/north.json"),
        ("settings/north.json", "settings/north.json"),
    ],
)
def test_profiles_are_resolved_from_config_directory(
    tmp_path, profile_reference, profile_location
):
    config_path = tmp_path / "custom-config.json"
    profile_path = tmp_path / profile_location
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(
        json.dumps({"linkedin": {}, "adzuna": {}}), encoding="utf-8"
    )
    config = {
        "profiles": {"north": profile_reference},
        "global_keywords": ["Engineer"],
    }

    [profile] = main.load_all_profiles(config, config_path)

    assert profile["profile_name"] == "north"
    assert profile["linkedin"]["keywords"] == ["Engineer"]
    assert profile["adzuna"]["keywords"] == ["Engineer"]
