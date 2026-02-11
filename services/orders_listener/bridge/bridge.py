import logging
import os
import time
from typing import Any

import requests
from google.cloud import firestore


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Missing required env var: {name}")
    return value


PROJECT_ID = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT", "demo-inventory")
ORDERS_COLLECTION = os.getenv("ORDERS_COLLECTION", "Orders")
FUNCTIONS_URL = _get_env("FUNCTIONS_URL", "http://orders_listener:8080/")

logging.basicConfig(level=logging.INFO, format="[bridge] %(message)s")


def _to_fields(data: dict[str, Any]) -> dict[str, dict[str, str]]:
    fields: dict[str, dict[str, str]] = {}
    for key, value in data.items():
        fields[key] = {"stringValue": str(value)}
    return fields


def _send_event(doc_id: str, data: dict[str, Any]) -> None:
    payload = {
        "value": {
            "name": f"projects/{PROJECT_ID}/databases/(default)/documents/{ORDERS_COLLECTION}/{doc_id}",
            "fields": _to_fields(data),
        }
    }
    response = requests.post(FUNCTIONS_URL, json=payload, timeout=10)
    logging.info("POST %s -> %s", doc_id, response.status_code)
    if response.text:
        logging.info("Response: %s", response.text)


def main() -> None:
    logging.info("Starting Firestore bridge")
    logging.info("Project: %s", PROJECT_ID)
    logging.info("Collection: %s", ORDERS_COLLECTION)
    logging.info("Functions URL: %s", FUNCTIONS_URL)

    client = firestore.Client(project=PROJECT_ID)
    collection = client.collection(ORDERS_COLLECTION)

    seen_ids: set[str] = set()
    poll_interval = float(os.getenv("BRIDGE_POLL_INTERVAL", "2"))
    initialized = False

    while True:
        try:
            docs = list(collection.stream())
            if not initialized:
                for doc in docs:
                    seen_ids.add(doc.id)
                initialized = True
                logging.info("Initialized polling with %d docs", len(seen_ids))
            else:
                for doc in docs:
                    if doc.id in seen_ids:
                        continue
                    seen_ids.add(doc.id)
                    data = doc.to_dict() or {}
                    logging.info("New order detected: %s", doc.id)
                    _send_event(doc.id, data)
        except Exception as exc:
            logging.info("Polling error: %s", exc)

        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
