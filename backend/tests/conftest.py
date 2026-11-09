import os

os.environ["WILLO_HOY"] = "2026-11-08"
os.environ["WILLO_TOOL_TOKEN"] = ""  # vacío: el .env de tu ordenador no lo pisa en los tests

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import store


@pytest.fixture()
def client():
    store.reset()
    return TestClient(app)
