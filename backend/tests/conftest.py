import os

os.environ["WILLO_HOY"] = "2026-11-08"
os.environ.pop("WILLO_TOOL_TOKEN", None)

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import store


@pytest.fixture()
def client():
    store.reset()
    return TestClient(app)
