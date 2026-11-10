from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.merchant_service import MerchantService
router=APIRouter(prefix="/merchants",tags=["Merchants"])
@router.get("")
def merchants(db:Session=Depends(get_db),_user=Depends(get_current_user)):
    return MerchantService.list_active_merchants(db)
