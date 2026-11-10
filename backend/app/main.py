from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine, SessionLocal, ensure_transaction_cashback_status_column
from app.services.seed_service import seed_demo_data
from app.api import auth, wallet, merchants, payments, reconciliation

app = FastAPI(
    title="FinPay API",
    description="Campus digital wallet and cashback – educational MVP",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    ensure_transaction_cashback_status_column()
    with SessionLocal() as db:
        seed_demo_data(db)

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "FinPay"}

for router in [auth.router, wallet.router, merchants.router, payments.router, reconciliation.router]:
    app.include_router(router, prefix="/api")
