from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from deps import require_user
from services.inventory import place_order

router = APIRouter()


class PlaceOrderRequest(BaseModel):
    buyer_email: EmailStr
    product_id: str


@router.post("/place")
def place(req: PlaceOrderRequest, user=Depends(require_user)):
    success = place_order(req.buyer_email, req.product_id)
    if not success:
        raise HTTPException(status_code=409, detail="Out of stock")
    return {"status": "order placed"}
