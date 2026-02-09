from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from services.users import create_user, authenticate_user
from security.jwt import create_token

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(req: RegisterRequest):
    create_user(req.email, req.password)
    return {"message": "user created"}


@router.post("/login")
def login(req: LoginRequest):
    user_id = authenticate_user(req.email, req.password)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": user_id, "email": req.email})
    return {"access_token": token}
