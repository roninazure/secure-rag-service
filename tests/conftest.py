# tests/conftest.py

import os
import sys

# add project root (one level up) to Python’s import path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
        )
    ),
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from src.main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)
