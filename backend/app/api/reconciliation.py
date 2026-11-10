from datetime import datetime
from fastapi import APIRouter,Depends,Query,HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.services.reconciliation_service import ReconciliationService
router=APIRouter(prefix="/reconciliation",tags=["Reconciliation"])
@router.get("/monthly")
def monthly(year:int=Query(default_factory=lambda:datetime.now().year,ge=2000,le=2100),
            month:int=Query(default_factory=lambda:datetime.now().month,ge=1,le=12),
            db:Session=Depends(get_db),_admin=Depends(require_role("ADMIN"))):
    try: return ReconciliationService.monthly_summary(db,year,month)
    except ValueError as e: raise HTTPException(422,str(e))
