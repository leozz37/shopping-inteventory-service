import time
import uuid

import requests


def _clear_mailhog(mailhog_url: str) -> None:
    requests.delete(f"{mailhog_url}/api/v1/messages", timeout=10)


def _wait_for_email(mailhog_url: str, to_email: str, timeout_seconds: int = 15) -> dict:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        response = requests.get(f"{mailhog_url}/api/v2/messages", timeout=10)
        response.raise_for_status()
        data = response.json()
        for item in data.get("items", []):
            to_header = item.get("Content", {}).get("Headers", {}).get("To", [])
            if any(to_email in value for value in to_header):
                return item
        time.sleep(0.5)
    raise AssertionError(f"No email delivered to {to_email} within {timeout_seconds}s")


def test_full_integration_flow(base_url: str, mailhog_url: str) -> None:
    _clear_mailhog(mailhog_url)

    email = f"user-{uuid.uuid4().hex[:8]}@example.com"
    password = "MySecurePass123"

    register_body = {"email": email, "password": password}
    response = requests.post(f"{base_url}/auth/register", json=register_body, timeout=15)
    assert response.status_code == 200, response.text

    login_body = {"email": email, "password": password}
    response = requests.post(f"{base_url}/auth/login", json=login_body, timeout=15)
    assert response.status_code == 200, response.text
    token = response.json().get("access_token")
    assert token

    order_body = {"buyer_email": email, "product_id": "product-1"}
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{base_url}/orders/place", json=order_body, headers=headers, timeout=15)
    assert response.status_code == 200, response.text

    delivered = _wait_for_email(mailhog_url, email)
    assert delivered.get("Content", {}).get("Headers", {}).get("To")
