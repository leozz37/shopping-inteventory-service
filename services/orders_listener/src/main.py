import logging

from .firestore_client import get_db
from .email_client import send_email
from .config import PRODUCTS_COLLECTION


def orders_listener(event, context):
    logging.info(f"Event received: {event}")

    value = event.get("value") if event else {}
    fields = value.get("fields") if value else {}

    buyer_email = _get_string(fields, "buyer_email")
    product_id = _get_string(fields, "product_id")

    if not buyer_email:
        logging.info("Error: Missing buyer_email in event fields")
        return

    if not product_id:
        logging.info("Error: Missing product_id in event fields")
        return

    db = get_db()
    try:
        product_doc = db.collection(PRODUCTS_COLLECTION).document(product_id).get()
        if not product_doc.exists:
            logging.info(f"LookupError: Product not found: {product_id}")
            return

        product = product_doc.to_dict() or {}
        product_name = product.get("product_name", product_id)

        subject = f"New order for product {product_name}"
        body = f"Your order was confirmed for product: {product_name}"

        send_email(buyer_email, subject, body)
        logging.info(f"Email sent successfully to {buyer_email}")

    except Exception as e:
        logging.info(f"Internal Error: {e}")
        raise e


def orders_listener_http(request):
    event = request.get_json(silent=True) or {}
    orders_listener(event, None)
    return ("", 204)


def _get_string(fields: dict, name: str) -> str | None:
    field_data = fields.get(name)
    if isinstance(field_data, dict) and "stringValue" in field_data:
        return field_data.get("stringValue")
    return None
