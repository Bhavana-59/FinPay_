from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="STUDENT", nullable=False)
    wallet: Mapped["Wallet"] = relationship(back_populates="student", uselist=False)

class Wallet(Base):
    __tablename__ = "wallets"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    balance_paise: Mapped[int] = mapped_column(Integer, default=0)
    tier: Mapped[str] = mapped_column(String(20), default="BASIC")
    student: Mapped[User] = relationship(back_populates="wallet")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="wallet")
    __table_args__ = (CheckConstraint("balance_paise >= 0"), CheckConstraint("tier IN ('BASIC','PRIME','PREMIUM')"))

class Merchant(Base):
    __tablename__ = "merchants"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="merchant")
    __table_args__ = (CheckConstraint("category IN ('CANTEEN','STATIONERY','TRANSPORT','HOSTEL','ONLINE')"),)

class CashbackRule(Base):
    __tablename__ = "cashback_rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(30), unique=True)
    rate_basis_points: Mapped[int] = mapped_column(Integer)
    monthly_cap_paise: Mapped[int] = mapped_column(Integer)

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), index=True)
    merchant_id: Mapped[int | None] = mapped_column(ForeignKey("merchants.id"), nullable=True)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    cashback_paise: Mapped[int] = mapped_column(Integer, default=0)
    cashback_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="SUCCESS")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    wallet: Mapped[Wallet] = relationship(back_populates="transactions")
    merchant: Mapped[Merchant | None] = relationship(back_populates="transactions")
    __table_args__ = (
        CheckConstraint("amount_paise > 0"),
        CheckConstraint("cashback_paise >= 0"),
        CheckConstraint("transaction_type IN ('PAYMENT','TOP_UP')"),
        Index("ix_tx_wallet_category_created", "wallet_id", "category", "created_at"),
    )
