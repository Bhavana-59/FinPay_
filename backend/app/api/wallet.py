from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.wallet_service import WalletService
router=APIRouter(prefix="/wallet",tags=["Wallet"])
@router.get("/me")
def my_wallet(db:Session=Depends(get_db),user=Depends(get_current_user)):
    if user.role!="STUDENT": raise HTTPException(403,"Student account required")
    wallet=WalletService.get_student_wallet(db,user.id)
    if not wallet: raise HTTPException(404,"Wallet not found")
    return {"id":wallet.id,"balance_paise":wallet.balance_paise,"tier":wallet.tier}
