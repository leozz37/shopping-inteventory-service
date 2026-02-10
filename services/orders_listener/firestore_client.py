from google.cloud import firestore
from .config import PROJECT_ID


def get_db() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)
