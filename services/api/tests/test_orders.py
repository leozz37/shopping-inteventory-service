from fastapi import HTTPException

def test_place_order_success(client, monkeypatch):
    def fake_place_order(buyer_email: str, product_id: str) -> bool:
        assert buyer_email == "leo@example.com"
        assert product_id == "product-1"
        return True

    from src.deps import require_user
    from src.main import app
    import src.routers.orders

    # Override the dependency
    async def fake_require_user_override(creds=None):
        return {"sub": "user-123"}
    
    app.dependency_overrides[require_user] = fake_require_user_override
    monkeypatch.setattr(src.routers.orders, "place_order", fake_place_order)

    resp = client.post("/orders/place", json={"buyer_email": "leo@example.com", "product_id": "product-1"})
    assert resp.status_code == 200
    assert resp.json() == {"status": "order placed"}


def test_place_order_out_of_stock(client, monkeypatch):
    def fake_place_order(buyer_email: str, product_id: str) -> bool:
        return False

    from src.deps import require_user
    from src.main import app
    import src.routers.orders

    # Override the dependency
    async def fake_require_user_override(creds=None):
        return {"sub": "user-123"}
    
    app.dependency_overrides[require_user] = fake_require_user_override
    monkeypatch.setattr(src.routers.orders, "place_order", fake_place_order)

    resp = client.post("/orders/place", json={"buyer_email": "leo@example.com", "product_id": "product-1"})
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Out of stock"

def test_place_order_missing_token_401(client):
    resp = client.post("/orders/place", json={"buyer_email": "leo@example.com", "product_id": "product-1"})
    assert resp.status_code in (401, 403)
