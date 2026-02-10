from fastapi import FastAPI
from src.routers import health, auth, orders

app = FastAPI(title="Inventory API")

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
