import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present (local dev)
ENV_PATH = Path(".env")
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)


def _required(name: str):
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


GCP_PROJECT_ID = _required("GCP_PROJECT_ID")
JWT_SECRET = _required("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
