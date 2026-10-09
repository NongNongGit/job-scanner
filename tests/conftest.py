import json
import os
import pytest


@pytest.fixture
def base_config():
    with open("config.json") as f:
        return json.load(f)


@pytest.fixture
def nz_profile():
    with open("profiles/NZ.json") as f:
        return json.load(f)
