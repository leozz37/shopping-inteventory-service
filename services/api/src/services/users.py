from src.services.firestore import users_ref
from src.security.password import hash_password, verify_password


def create_user(email: str, password: str):
    users_ref().document(email).set({"password": hash_password(password)})


def authenticate_user(email: str, password: str):
    doc = users_ref().document(email).get()
    if not doc.exists:
        return None
    if not verify_password(password, doc.to_dict()["password"]):
        return None
    return email
