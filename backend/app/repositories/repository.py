from sqlalchemy import select, func
from app.models.models import User, Wallet, Merchant, CashbackRule, Transaction
class UserRepository:
    @staticmethod
    def by_email(db, email):
        return db.scalar(select(User).where(User.email == email.lower()))
class WalletRepository:
    @staticmethod
    def by_student(db, student_id):
        return db.scalar(select(Wallet).where(Wallet.student_id == student_id))
class MerchantRepository:
    @staticmethod
    def active(db):
        return list(db.scalars(select(Merchant).where(Merchant.is_active.is_(True)).order_by(Merchant.name)))
    @staticmethod
    def by_id(db, merchant_id):
        return db.get(Merchant, merchant_id)
class CashbackRepository:
    @staticmethod
    def by_category(db, category):
        return db.scalar(select(CashbackRule).where(CashbackRule.category == category))
    @staticmethod
    def earned(db, wallet_id, category, start, end):
        q = select(func.coalesce(func.sum(Transaction.cashback_paise), 0)).where(
            Transaction.wallet_id == wallet_id, Transaction.category == category,
            Transaction.transaction_type == "PAYMENT", Transaction.status == "SUCCESS",
            Transaction.created_at >= start, Transaction.created_at < end)
        return int(db.scalar(q) or 0)
class TransactionRepository:
    @staticmethod
    def by_key(db, key):
        return db.scalar(select(Transaction).where(Transaction.idempotency_key == key))
    @staticmethod
    def history(db, wallet_id):
        return list(db.scalars(select(Transaction).where(Transaction.wallet_id == wallet_id)
            .order_by(Transaction.created_at.desc(), Transaction.id.desc()).limit(50)))
