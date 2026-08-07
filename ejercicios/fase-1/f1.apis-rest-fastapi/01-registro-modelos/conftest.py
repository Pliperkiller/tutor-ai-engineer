import os

os.environ["MODEL_REGISTRY_API_KEY"] = "dev-secret-key"

import pytest
from fastapi.testclient import TestClient

from main import MODELS, app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_models_store():
    original = MODELS.copy()
    yield
    MODELS.clear()
    MODELS.update(original)
