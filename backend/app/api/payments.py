from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.repositories.repository import WalletRepository,TransactionRepository
from app.schemas.schemas import PaymentRequest,TopUpRequest,PaymentResult
from app.services.cashback_service import NOT_APPLICABLE
from app.services.payment_service import PaymentService
router=APIRouter(prefix="/payments",tags=["Payments"])
@router.post("",response_model=PaymentResult)
def pay(payload:PaymentRequest,db:Session=Depends(get_db),user=Depends(get_current_user)):
    if user.role!="STUDENT": raise HTTPException(403,"Student account required")
    return PaymentService.process_payment(db,user.id,payload.merchant_id,payload.amount_paise,payload.idempotency_key)
@router.post("/top-up",response_model=PaymentResult)
def topup(payload:TopUpRequest,db:Session=Depends(get_db),user=Depends(get_current_user)):
    if user.role!="STUDENT": raise HTTPException(403,"Student account required")
    return PaymentService.top_up(db,user.id,payload.amount_paise,payload.idempotency_key)
@router.get("/history")
def history(db:Session=Depends(get_db),user=Depends(get_current_user)):
    if user.role!="STUDENT": raise HTTPException(403,"Student account required")
    wallet=WalletRepository.by_student(db,user.id)
    if not wallet: raise HTTPException(404,"Wallet not found")
    return [{"id":t.id,"transaction_type":t.transaction_type,"category":t.category,
      "amount_paise":t.amount_paise,"cashback_paise":t.cashback_paise,"status":t.status,
      "cashback_status":t.cashback_status or (
          NOT_APPLICABLE if t.transaction_type == "TOP_UP"
          else "Cashback status unavailable"
      ),
      "idempotency_key":t.idempotency_key,"created_at":t.created_at.isoformat()}
      for t in TransactionRepository.history(db,wallet.id)]
