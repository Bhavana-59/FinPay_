from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models.models import Transaction
from app.repositories.repository import WalletRepository, MerchantRepository, CashbackRepository, TransactionRepository
from app.services.cashback_service import (
    NOT_APPLICABLE,
    cashback_status,
    calculate_cashback,
)

def month_window(now):
    start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    end = datetime(now.year + (now.month == 12), 1 if now.month == 12 else now.month + 1, 1, tzinfo=timezone.utc)
    return start, end

class PaymentService:
    @staticmethod
    def _result(tx, wallet, replayed):
        return {"transaction_id":tx.id, "transaction_type":tx.transaction_type,
                "amount_paise":tx.amount_paise, "cashback_paise":tx.cashback_paise,
                "cashback_status": tx.cashback_status or (
                    NOT_APPLICABLE if tx.transaction_type == "TOP_UP"
                    else "Cashback status unavailable"
                ),
                "wallet_balance_paise":wallet.balance_paise, "tier":wallet.tier, "replayed":replayed}

    @staticmethod
    def _existing(db, student_id, key):
        tx = TransactionRepository.by_key(db, key)
        if not tx:
            return None
        if tx.wallet.student_id != student_id:
            raise HTTPException(409, "Idempotency key already belongs to another user")
        return PaymentService._result(tx, WalletRepository.by_student(db, student_id), True)

    @staticmethod
    def process_payment(db, student_id, merchant_id, amount_paise, key):
        replay = PaymentService._existing(db, student_id, key)
        if replay: return replay
        wallet = WalletRepository.by_student(db, student_id)
        merchant = MerchantRepository.by_id(db, merchant_id)
        if not wallet: raise HTTPException(404, "Wallet not found")
        if not merchant or not merchant.is_active: raise HTTPException(404, "Merchant unavailable")
        if amount_paise <= 0: raise HTTPException(422, "Amount must be positive")
        if wallet.balance_paise < amount_paise: raise HTTPException(400, "Insufficient wallet balance")
        rule = CashbackRepository.by_category(db, merchant.category)
        if not rule: raise HTTPException(500, "Cashback rule missing")
        now = datetime.now(timezone.utc)
        quote = calculate_cashback(amount_paise, rule.rate_basis_points, rule.monthly_cap_paise, wallet.tier)
        start, end = month_window(now)
        earned = CashbackRepository.earned(db, wallet.id, merchant.category, start, end)
        awarded = min(quote.raw_cashback_paise, max(0, quote.tier_monthly_cap_paise - earned))
        status = cashback_status(
            quote.raw_cashback_paise,
            awarded,
            earned,
            quote.tier_monthly_cap_paise,
        )
        try:
            wallet.balance_paise += -amount_paise + awarded
            tx = Transaction(wallet_id=wallet.id, merchant_id=merchant.id, transaction_type="PAYMENT",
                category=merchant.category, amount_paise=amount_paise, cashback_paise=awarded,
                cashback_status=status, idempotency_key=key, status="SUCCESS", created_at=now)
            db.add(tx); db.commit(); db.refresh(tx); db.refresh(wallet)
            return PaymentService._result(tx, wallet, False)
        except IntegrityError:
            db.rollback()
            replay = PaymentService._existing(db, student_id, key)
            if replay: return replay
            raise HTTPException(409, "Duplicate idempotency key")
        except Exception:
            db.rollback(); raise

    @staticmethod
    def top_up(db, student_id, amount_paise, key):
        replay = PaymentService._existing(db, student_id, key)
        if replay: return replay
        wallet = WalletRepository.by_student(db, student_id)
        if not wallet: raise HTTPException(404, "Wallet not found")
        if amount_paise <= 0: raise HTTPException(422, "Amount must be positive")
        try:
            wallet.balance_paise += amount_paise
            tx = Transaction(wallet_id=wallet.id, merchant_id=None, transaction_type="TOP_UP",
                category="TOP_UP", amount_paise=amount_paise, cashback_paise=0,
                cashback_status=NOT_APPLICABLE, idempotency_key=key, status="SUCCESS",
                created_at=datetime.now(timezone.utc))
            db.add(tx); db.commit(); db.refresh(tx); db.refresh(wallet)
            return PaymentService._result(tx, wallet, False)
        except IntegrityError:
            db.rollback()
            replay = PaymentService._existing(db, student_id, key)
            if replay: return replay
            raise HTTPException(409, "Duplicate idempotency key")
        except Exception:
            db.rollback(); raise
