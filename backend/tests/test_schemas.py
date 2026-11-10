import pytest
from pydantic import ValidationError

from app.schemas.schemas import LoginRequest


def test_login_accepts_demo_local_email():
    request = LoginRequest(email="rahul@finpay.local", password="Student@123")

    assert request.email == "rahul@finpay.local"


def test_login_normalizes_regular_email():
    request = LoginRequest(email="Student@Example.com", password="password")

    assert request.email == "Student@example.com"


def test_login_rejects_malformed_email():
    with pytest.raises(ValidationError):
        LoginRequest(email="not-an-email", password="password")
