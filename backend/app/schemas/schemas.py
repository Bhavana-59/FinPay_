from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, Field, ConfigDict, field_validator
class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_login_email(cls, value: str) -> str:
        local_part, separator, domain = value.strip().rpartition("@")
        if not separator:
            raise ValueError("Invalid email address")

        is_demo_email = domain.lower() == "finpay.local"
        address_to_validate = (
            f"{local_part}@finpay.example.com" if is_demo_email else value.strip()
        )
        try:
            validated = validate_email(address_to_validate, check_deliverability=False)
        except EmailNotValidError as error:
            raise ValueError(str(error)) from error

        if is_demo_email:
            return f"{validated.local_part}@finpay.local"
        return validated.normalized

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str
class PaymentRequest(BaseModel):
    merchant_id: int
    amount_paise: int = Field(gt=0, le=100000000)
    idempotency_key: str = Field(min_length=8, max_length=100)
class TopUpRequest(BaseModel):
    amount_paise: int = Field(gt=0, le=100000000)
    idempotency_key: str = Field(min_length=8, max_length=100)
class WalletOut(BaseModel):
    id: int
    balance_paise: int
    tier: str
    model_config = ConfigDict(from_attributes=True)
class PaymentResult(BaseModel):
    transaction_id: int
    transaction_type: str
    amount_paise: int
    cashback_paise: int
    cashback_status: str
    wallet_balance_paise: int
    tier: str
    replayed: bool = False
