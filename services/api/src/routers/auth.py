from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/register")
def register(email: str, password: str):
    # TODO: create email method

    return {"message": "user created"}

@router.post("/login")
def login(email: str, password: str):
    # TODO: auth user
    user_id = "hello world"
    if not user_id:
        raise HTTPException(status_code=401)
    # TODO: create token

    return {"access_token": "hello world"}
