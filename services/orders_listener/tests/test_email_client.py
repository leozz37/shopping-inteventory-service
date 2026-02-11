def test_send_email_success(monkeypatch):
    from src.email_client import send_email
    
    smtp_calls = []
    
    class MockSMTP:
        def __init__(self, host, port, timeout=None):
            self.host = host
            self.port = port
            
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
        
        def ehlo(self):
            smtp_calls.append("ehlo")
        
        def starttls(self):
            smtp_calls.append("starttls")
        
        def login(self, user, password):
            smtp_calls.append(("login", user, password))
        
        def send_message(self, msg):
            smtp_calls.append(("send_message", str(msg)))
    
    import smtplib
    monkeypatch.setattr(smtplib, "SMTP", MockSMTP)
    
    send_email(
        to_email="recipient@example.com",
        subject="Test Subject",
        body="Test Body"
    )
    
    assert len(smtp_calls) > 0
    assert "ehlo" in smtp_calls
    assert "starttls" in smtp_calls


def test_send_email_verifies_credentials(monkeypatch):
    from src.email_client import send_email
    
    login_called = {}
    
    class MockSMTP:
        def __init__(self, host, port, timeout=None):
            pass
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
        
        def ehlo(self):
            pass
        
        def starttls(self):
            pass
        
        def login(self, user, password):
            login_called["user"] = user
            login_called["password"] = password
        
        def send_message(self, msg):
            pass
    
    import smtplib
    monkeypatch.setattr(smtplib, "SMTP", MockSMTP)
    
    send_email(
        to_email="recipient@example.com",
        subject="Test",
        body="Test"
    )
    
    assert login_called["user"] == "test@example.com"
    assert login_called["password"] == "test-password"


def test_send_email_sets_headers(monkeypatch):
    from src.email_client import send_email
    
    sent_messages = []
    
    class MockSMTP:
        def __init__(self, host, port, timeout=None):
            pass
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
        
        def ehlo(self):
            pass
        
        def starttls(self):
            pass
        
        def login(self, user, password):
            pass
        
        def send_message(self, msg):
            sent_messages.append({
                "from": msg["From"],
                "to": msg["To"],
                "subject": msg["Subject"]
            })
    
    import smtplib
    monkeypatch.setattr(smtplib, "SMTP", MockSMTP)
    
    send_email(
        to_email="recipient@example.com",
        subject="Test Subject",
        body="Test Body"
    )
    
    assert len(sent_messages) == 1
    assert sent_messages[0]["to"] == "recipient@example.com"
    assert sent_messages[0]["subject"] == "Test Subject"
    assert sent_messages[0]["from"] == "test@example.com"
