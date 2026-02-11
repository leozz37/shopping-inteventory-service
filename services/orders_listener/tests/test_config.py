import pytest


def test_config_loads_required_env_vars():
    import src.config as config
    
    assert config.SMTP_HOST == "smtp.gmail.com"
    assert config.SMTP_PORT == 587
    assert config.SMTP_USER == "test@example.com"
    assert config.SMTP_PASSWORD == "test-password"
    assert config.SMTP_FROM == "test@example.com"


def test_config_smtp_use_tls():
    import src.config as config
    
    assert config.SMTP_USE_TLS is True


def test_config_gcp_project_id():
    import src.config as config
    
    assert config.PROJECT_ID == "test-project"


def test_config_collections():
    import src.config as config
    
    assert config.ORDERS_COLLECTION == "Orders"
    assert config.PRODUCTS_COLLECTION == "Products"


def test_config_missing_required_env_var(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    
    # Force reload of config to test missing env var
    import sys
    if "src.config" in sys.modules:
        del sys.modules["src.config"]
    
    with pytest.raises(RuntimeError, match="Missing required env var"):
        import src.config
