import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

os.environ.setdefault("GCP_PROJECT_ID", "test-project")
os.environ.setdefault("SMTP_HOST", "smtp.gmail.com")
os.environ.setdefault("SMTP_PORT", "587")
os.environ.setdefault("SMTP_USER", "test@example.com")
os.environ.setdefault("SMTP_PASSWORD", "test-password")
os.environ.setdefault("SMTP_FROM", "test@example.com")
os.environ.setdefault("SMTP_USE_TLS", "true")
os.environ.setdefault("ORDERS_COLLECTION", "Orders")
os.environ.setdefault("PRODUCTS_COLLECTION", "Products")


def pytest_configure(config):
    class MockDocSnapshot:
        def __init__(self, data=None, exists=True):
            self._data = data or {}
            self.exists = exists
        
        def to_dict(self):
            return self._data
    
    class MockDocRef:
        def __init__(self):
            self._data = None

        def get(self, transaction=None):
            exists = bool(self._data)
            return MockDocSnapshot(self._data or {}, exists=exists)

        def set(self, data, **kwargs):
            self._data = data
    
    class MockCollRef:
        def __init__(self):
            self._docs = {}
        
        def document(self, doc_id=None):
            if doc_id not in self._docs:
                self._docs[doc_id] = MockDocRef()
            return self._docs[doc_id]
    
    class MockClient:
        def __init__(self, **kwargs):
            self._collections = {}
        
        def collection(self, name):
            if name not in self._collections:
                self._collections[name] = MockCollRef()
            return self._collections[name]
    
    # Create a single MockClient instance so repeated get_db() calls share state
    _singleton_mock_client = MockClient()

    class MockFirestore:
        def Client(self, **kwargs):
            return _singleton_mock_client

    sys.modules["google.cloud.firestore"] = MockFirestore()


@pytest.fixture(autouse=True)
def _test_env(monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "test@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "test-password")
    monkeypatch.setenv("SMTP_FROM", "test@example.com")
    monkeypatch.setenv("SMTP_USE_TLS", "true")
    monkeypatch.setenv("ORDERS_COLLECTION", "Orders")
    monkeypatch.setenv("PRODUCTS_COLLECTION", "Products")
