import src.main as main


def test_orders_listener_success(monkeypatch):
    email_sent = {}
    
    def fake_send_email(to_email: str, subject: str, body: str) -> None:
        email_sent["to"] = to_email
        email_sent["subject"] = subject
        email_sent["body"] = body
    
    monkeypatch.setattr(main, "send_email", fake_send_email)
    main.orders_listener.__globals__["send_email"] = fake_send_email
    
    event = {
        "value": {
            "fields": {
                "buyer_email": {"stringValue": "buyer@example.com"},
                "product_id": {"stringValue": "product-123"}
            }
        }
    }
    
    from src.firestore_client import get_db
    mock_db = get_db()
    products_collection = mock_db.collection("Products")
    product_doc = products_collection.document("product-123")
    product_doc.set({"name": "Test Product"})

    main.orders_listener(event, None)
    
    assert email_sent["to"] == "buyer@example.com"
    assert "product-123" in email_sent["subject"]


def test_orders_listener_missing_buyer_email(monkeypatch, capsys):
    monkeypatch.setattr(main, "send_email", lambda *args: None)
    main.orders_listener.__globals__["send_email"] = lambda *args: None
    
    event = {
        "value": {
            "fields": {
                "product_id": {"stringValue": "product-123"}
            }
        }
    }
    
    main.orders_listener(event, None)
    captured = capsys.readouterr()


def test_orders_listener_missing_product_id(monkeypatch):
    monkeypatch.setattr(main, "send_email", lambda *args: None)
    main.orders_listener.__globals__["send_email"] = lambda *args: None
    
    event = {
        "value": {
            "fields": {
                "buyer_email": {"stringValue": "buyer@example.com"}
            }
        }
    }
    
    main.orders_listener(event, None)


def test_orders_listener_product_not_found(monkeypatch):
    from src.firestore_client import get_db

    mock_db = get_db()

    def fake_send_email(*args):
        raise AssertionError("Email should not be sent if product doesn't exist")
    
    monkeypatch.setattr(main, "send_email", fake_send_email)
    main.orders_listener.__globals__["send_email"] = fake_send_email
    
    products_collection = mock_db.collection("Products")
    product_doc = products_collection.document("nonexistent")
    
    event = {
        "value": {
            "fields": {
                "buyer_email": {"stringValue": "buyer@example.com"},
                "product_id": {"stringValue": "nonexistent"}
            }
        }
    }
    
    main.orders_listener(event, None)


def test_get_string_with_valid_data():
    fields = {
        "name": {"stringValue": "John"}
    }
    
    result = main._get_string(fields, "name")
    assert result == "John"


def test_get_string_with_missing_key():
    fields = {
        "name": {"stringValue": "John"}
    }
    
    result = main._get_string(fields, "age")
    assert result is None


def test_get_string_with_invalid_format():
    fields = {
        "name": {"intValue": 123}
    }
    
    result = main._get_string(fields, "name")
    assert result is None
