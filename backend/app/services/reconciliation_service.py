from datetime import datetime, timezone
from sqlalchemy import select
from app.models.models import Transaction
class ReconciliationService:
    @staticmethod
    def monthly_summary(db, year, month):
        if not 1 <= month <= 12: raise ValueError("month must be 1..12")
        start = datetime(year, month, 1, tzinfo=timezone.utc)
        end = datetime(year + (month == 12), 1 if month == 12 else month + 1, 1, tzinfo=timezone.utc)
        rows = list(db.scalars(select(Transaction).where(Transaction.created_at >= start,
            Transaction.created_at < end, Transaction.status == "SUCCESS")))
        payments = [x for x in rows if x.transaction_type == "PAYMENT"]
        topups = [x for x in rows if x.transaction_type == "TOP_UP"]
        return {"year":year, "month":month, "transaction_count":len(rows),
            "payment_amount_paise":sum(x.amount_paise for x in payments),
            "topup_amount_paise":sum(x.amount_paise for x in topups),
            "cashback_awarded_paise":sum(x.cashback_paise for x in payments),
            "net_payment_count":len(payments)}
