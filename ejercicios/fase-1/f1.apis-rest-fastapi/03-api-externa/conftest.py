import os

os.environ["MODEL_REGISTRY_API_KEY"] = "dev-secret-key"

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from main import MODELS, app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_models_store() -> Iterator[None]:
    original = MODELS.copy()
    yield
    MODELS.clear()
    MODELS.update(original)
