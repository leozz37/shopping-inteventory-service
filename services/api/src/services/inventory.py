from google.cloud import firestore
from src.services.firestore import products_ref, orders_ref

db = firestore.Client()


def place_order(buyer_email: str, product_id: str) -> bool:
    product_doc = products_ref().document(product_id)

    @firestore.transactional
    def txn(txn):
        snap = product_doc.get(transaction=txn)
        if not snap.exists:
            return False

        data = snap.to_dict()
        if data["quantity"] <= 0:
            return False

        new_qty = data["quantity"] - 1
        status = "out_of_stock" if new_qty == 0 else "in_stock"

        txn.update(product_doc, {"quantity": new_qty, "status": status})

        txn.set(
            orders_ref().document(),
            {"buyer_email": buyer_email, "product_id": product_id},
        )

        return True

    return txn(db.transaction())
