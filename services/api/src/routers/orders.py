from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/place")
def place(buyer_email: str, product_id: str):
    # TODO: place order
    success = "hello world"

    if not success:
        raise HTTPException(status_code=409, detail="Out of stock")
    
    return {"status": "order placed"}
