from fastapi import APIRouter, HTTPException
from services.users import create_user, authenticate_user
from security.jwt import create_token

router = APIRouter()


@router.post("/register")
def register(email: str, password: str):
    create_user(email, password)
    return {"message": "user created"}


@router.post("/login")
def login(email: str, password: str):
    user_id = authenticate_user(email, password)
    if not user_id:
        raise HTTPException(status_code=401)

    token = create_token({"sub": user_id, "email": email})
    return {"access_token": token}
