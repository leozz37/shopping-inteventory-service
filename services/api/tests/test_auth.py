def test_register_success(client, monkeypatch):
    calls = {"n": 0}

    def fake_create_user(email: str, password: str):
        calls["n"] += 1
        assert email == "leo@example.com"
        assert password == "pass123"

    # Patch at the router level where it's imported
    import src.routers.auth
    monkeypatch.setattr(src.routers.auth, "create_user", fake_create_user)

    resp = client.post("/auth/register", json={"email": "leo@example.com", "password": "pass123"})
    assert resp.status_code == 200
    assert resp.json() == {"message": "user created"}
    assert calls["n"] == 1


def test_login_success_returns_token(client, monkeypatch):
    def fake_authenticate_user(email: str, password: str):
        assert email == "leo@example.com"
        assert password == "pass123"
        return "user-123"

    def fake_create_token(claims: dict):
        # Validate expected claims are passed
        assert claims["sub"] == "user-123"
        assert claims["email"] == "leo@example.com"
        return "fake.jwt.token"

    import src.routers.auth
    monkeypatch.setattr(src.routers.auth, "authenticate_user", fake_authenticate_user)
    monkeypatch.setattr(src.routers.auth, "create_token", fake_create_token)

    resp = client.post("/auth/login", json={"email": "leo@example.com", "password": "pass123"})
    assert resp.status_code == 200
    assert resp.json() == {"access_token": "fake.jwt.token"}


def test_login_invalid_credentials(client, monkeypatch):
    def fake_authenticate_user(email: str, password: str):
        return None

    import src.routers.auth
    monkeypatch.setattr(src.routers.auth, "authenticate_user", fake_authenticate_user)

    resp = client.post("/auth/login", json={"email": "leo@example.com", "password": "wrong"})
    assert resp.status_code == 401
