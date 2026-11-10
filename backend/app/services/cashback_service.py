from dataclasses import dataclass
TIER_MULTIPLIERS = {"BASIC": (1, 1), "PRIME": (3, 2), "PREMIUM": (2, 1)}
NOT_APPLICABLE = "Not applicable"
CASHBACK_EARNED = "Cashback earned"
MONTHLY_CAP_REACHED = "Monthly cap limit reached"
MONTHLY_LIMIT_EXHAUSTED = "Monthly limit exhausted"
NO_CASHBACK_FOR_AMOUNT = "No cashback for this amount"

@dataclass(frozen=True)
class CashbackQuote:
    raw_cashback_paise: int
    tier_monthly_cap_paise: int

def cashback_status(raw_cashback_paise: int, awarded_paise: int, earned_paise: int,
                    monthly_cap_paise: int) -> str:
    if raw_cashback_paise == 0:
        return NO_CASHBACK_FOR_AMOUNT
    if earned_paise >= monthly_cap_paise:
        return MONTHLY_LIMIT_EXHAUSTED
    if awarded_paise < raw_cashback_paise:
        return MONTHLY_CAP_REACHED
    return CASHBACK_EARNED

def calculate_cashback(amount_paise: int, rate_basis_points: int, base_monthly_cap_paise: int, tier: str) -> CashbackQuote:
    # Integer-only calculation: 100 basis points = 1%; // applies floor.
    if min(amount_paise, rate_basis_points, base_monthly_cap_paise) < 0:
        raise ValueError("Inputs cannot be negative")
    if tier not in TIER_MULTIPLIERS:
        raise ValueError("Unknown wallet tier")
    num, den = TIER_MULTIPLIERS[tier]
    raw = (amount_paise * rate_basis_points * num) // (10000 * den)
    cap = (base_monthly_cap_paise * num) // den
    return CashbackQuote(raw, cap)
