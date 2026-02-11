from datetime import datetime, timezone
import os
from google.cloud import firestore

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "dshopping-inventory-service")
db = firestore.Client(project=PROJECT)

def main():
    # Products/{product_id}
    product_id = "product-1"
    db.collection("Products").document(product_id).set({
        "product_id": product_id,
        "product_name": "Demo Product",
        "quantity": 5,
        "status": "in_stock",
    })

    print("Seeded Firestore emulator: Products")

if __name__ == "__main__":
    main()
