def test_firestore_client_initialization():
    from src.firestore_client import get_db
    
    db = get_db()
    assert db is not None


def test_firestore_client_has_collection_method():
    from src.firestore_client import get_db
    
    db = get_db()
    assert hasattr(db, "collection")
    assert callable(db.collection)


def test_firestore_client_collection_retrieval():
    from src.firestore_client import get_db
    
    db = get_db()
    products_ref = db.collection("Products")
    
    assert products_ref is not None
    assert hasattr(products_ref, "document")
