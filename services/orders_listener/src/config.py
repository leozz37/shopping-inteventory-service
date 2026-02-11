import os


def env(name: str, default: str | None = None) -> str:
    val = os.getenv(name, default)
    if val is None or val == "":
        raise RuntimeError(f"Missing required env var: {name}")
    return val


SMTP_HOST = env("SMTP_HOST")
SMTP_PORT = int(env("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

SMTP_FROM = env("SMTP_FROM")
SMTP_USE_TLS = env("SMTP_USE_TLS", "true").lower() == "true"

PROJECT_ID = env("GCP_PROJECT_ID", "shopping-inventory-service")

ORDERS_COLLECTION = env("ORDERS_COLLECTION", "Orders")
PRODUCTS_COLLECTION = env("PRODUCTS_COLLECTION", "Products")
