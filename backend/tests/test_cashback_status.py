import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from app.api.payments import history as payment_history
from app.core.database import Base, ensure_transaction_cashback_status_column
from app.models.models import CashbackRule, Merchant, Transaction, User, Wallet
from app.services.cashback_service import (
    CASHBACK_EARNED,
    MONTHLY_CAP_REACHED,
    MONTHLY_LIMIT_EXHAUSTED,
    NO_CASHBACK_FOR_AMOUNT,
    NOT_APPLICABLE,
)
from app.services.payment_service import PaymentService


@pytest.fixture
def payment_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        user = User(
            name="Student",
            email="student@example.com",
            password_hash="unused",
            role="STUDENT",
        )
        db.add(user)
        db.flush()
        wallet = Wallet(student_id=user.id, balance_paise=100_000, tier="BASIC")
        merchant = Merchant(name="Canteen", category="CANTEEN", is_active=True)
        db.add_all([wallet, merchant])
        db.commit()
        yield db, user.id, merchant.id
    engine.dispose()


def set_cashback_rule(db, rate_basis_points, monthly_cap_paise):
    db.add(CashbackRule(
        category="CANTEEN",
        rate_basis_points=rate_basis_points,
        monthly_cap_paise=monthly_cap_paise,
    ))
    db.commit()


def make_payment(db, student_id, merchant_id, key):
    return PaymentService.process_payment(
        db, student_id, merchant_id, 10_000, key
    )

def assert_saved_status(db, student_id, transaction_id, expected_status):
    transaction = db.get(Transaction, transaction_id)
    assert transaction.cashback_status == expected_status
    history = payment_history(db, db.get(User, student_id))
    assert history[0]["cashback_status"] == expected_status


def test_full_cashback_is_recorded(payment_db):
    db, student_id, merchant_id = payment_db
    set_cashback_rule(db, rate_basis_points=200, monthly_cap_paise=5_000)

    result = make_payment(db, student_id, merchant_id, "full-cashback-001")

    assert result["cashback_status"] == CASHBACK_EARNED
    assert_saved_status(db, student_id, result["transaction_id"], CASHBACK_EARNED)


def test_partial_cashback_cap_reason_persists_on_idempotent_replay(payment_db):
    db, student_id, merchant_id = payment_db
    set_cashback_rule(db, rate_basis_points=200, monthly_cap_paise=100)

    first = make_payment(db, student_id, merchant_id, "partial-cashback-001")
    replay = make_payment(db, student_id, merchant_id, "partial-cashback-001")

    assert first["cashback_paise"] == 100
    assert first["cashback_status"] == MONTHLY_CAP_REACHED
    assert replay["cashback_status"] == MONTHLY_CAP_REACHED
    assert replay["replayed"] is True
    assert_saved_status(db, student_id, first["transaction_id"], MONTHLY_CAP_REACHED)


def test_exhausted_cap_reason(payment_db):
    db, student_id, merchant_id = payment_db
    set_cashback_rule(db, rate_basis_points=200, monthly_cap_paise=100)
    make_payment(db, student_id, merchant_id, "exhaust-cap-001")

    result = make_payment(db, student_id, merchant_id, "exhaust-cap-002")

    assert result["cashback_paise"] == 0
    assert result["cashback_status"] == MONTHLY_LIMIT_EXHAUSTED
    assert_saved_status(db, student_id, result["transaction_id"], MONTHLY_LIMIT_EXHAUSTED)


def test_zero_calculated_cashback_is_not_mislabeled_as_cap_exhaustion(payment_db):
    db, student_id, merchant_id = payment_db
    set_cashback_rule(db, rate_basis_points=0, monthly_cap_paise=5_000)

    result = make_payment(db, student_id, merchant_id, "zero-cashback-001")

    assert result["cashback_paise"] == 0
    assert result["cashback_status"] == NO_CASHBACK_FOR_AMOUNT
    assert_saved_status(db, student_id, result["transaction_id"], NO_CASHBACK_FOR_AMOUNT)


def test_top_up_status_is_not_applicable(payment_db):
    db, student_id, _ = payment_db

    result = PaymentService.top_up(db, student_id, 10_000, "top-up-status-001")

    assert result["cashback_status"] == NOT_APPLICABLE
    assert_saved_status(db, student_id, result["transaction_id"], NOT_APPLICABLE)


def test_existing_database_gets_nullable_status_column():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE transactions (id INTEGER PRIMARY KEY)"))

    ensure_transaction_cashback_status_column(engine)

    columns = {column["name"]: column for column in inspect(engine).get_columns(
        "transactions"
    )}
    assert columns["cashback_status"]["nullable"] is True
    engine.dispose()
