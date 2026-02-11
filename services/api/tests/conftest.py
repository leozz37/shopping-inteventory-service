import os
import sys
import pytest
from fastapi.testclient import TestClient


# Set test environment EARLY before any imports
os.environ.setdefault("GCP_PROJECT_ID", "test-project")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRES_MINUTES", "60")


def pytest_configure(config):
    """Pytest hook to set up mocks before test collection"""

    class MockClient:
        def collection(self, name):
            return self

        def document(self, doc_id=None):
            return self

        def get(self, transaction=None):
            return self

        def set(self, data, **kwargs):
            pass

        def transaction(self):
            return lambda func: func(self)

        def exists(self):
            return False

        def to_dict(self):
            return {}

    class MockFirestore:
        def Client(self, **kwargs):
            return MockClient()

    sys.modules["google.cloud.firestore"] = MockFirestore()


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
