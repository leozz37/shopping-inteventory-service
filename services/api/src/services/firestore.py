from google.cloud import firestore

db = firestore.Client()


def products_ref():
    return db.collection("Products")


def orders_ref():
    return db.collection("Orders")


def users_ref():
    return db.collection("Users")
