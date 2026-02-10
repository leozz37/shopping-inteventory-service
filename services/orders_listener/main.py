import functions_framework

from .firestore_client import get_db
from .email_client import send_email
from .config import PRODUCTS_COLLECTION


@functions_framework.cloud_event
def orders_listener(cloud_event):
    print("1. Start")

    data = cloud_event.data or {}
    value = data.get("value", {})
    fields = value.get("fields", {})
    
    buyer_email = _get_string(fields, "buyer_email")
    product_id = _get_string(fields, "product_id")
    print(f"2. Email received: {buyer_email}")

    if not buyer_email:
        raise ValueError("Missing buyer_email in Firestore event")

    if not product_id:
        raise ValueError("Missing product_id in Firestore event")

    db = get_db()
    print(f"3. Got DB")

    product_doc = db.collection(PRODUCTS_COLLECTION).document(product_id).get()
    if not product_doc.exists:
        raise LookupError(f"Product not found: {product_id}")

    print(f"4. Product found")
    product = product_doc.to_dict() or {}
    product_name = product.get("product_name", product_id)

    print(f"5. No product name")
    if not product_name:
        raise ValueError(f"Product {product_id} missing product_name")

    subject = f"New order for product {product_name}"
    body = f"Your order was confirmed for product: {product_name}\nProduct ID: {product_id}"

    print(f"6. Trying to send email")
    try:
        send_email(buyer_email, subject, body)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to send confirmation email to {buyer_email}"
        ) from exc
    print(f"7. Email sent")


def _get_string(fields: dict, name: str) -> str | None:
    v = fields.get(name)
    if not isinstance(v, dict):
        return None
    return v.get("stringValue")
