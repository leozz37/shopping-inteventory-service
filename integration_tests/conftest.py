import os

import pytest


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("INVENTORY_API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def mailhog_url() -> str:
    return os.getenv("MAILHOG_API_URL", "http://localhost:8025")
