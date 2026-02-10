import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _test_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_EXPIRES_MINUTES", "60")
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")


@pytest.fixture
def client():
    from src.main import app

    app.dependency_overrides.clear()
    return TestClient(app)
