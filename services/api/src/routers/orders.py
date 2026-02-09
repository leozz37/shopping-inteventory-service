from fastapi import APIRouter, Depends, HTTPException
from deps import require_user
from services.inventory import place_order

router = APIRouter()


@router.post("/place")
def place(buyer_email: str, product_id: str, user=Depends(require_user)):
    success = place_order(buyer_email, product_id)
    if not success:
        raise HTTPException(status_code=409, detail="Out of stock")
    return {"status": "order placed"}
