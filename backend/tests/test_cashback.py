import pytest
from app.services.cashback_service import calculate_cashback
def test_basic_canteen_100():
    q=calculate_cashback(10000,200,5000,"BASIC")
    assert (q.raw_cashback_paise,q.tier_monthly_cap_paise)==(200,5000)
def test_prime_multiplier():
    q=calculate_cashback(10000,200,5000,"PRIME")
    assert (q.raw_cashback_paise,q.tier_monthly_cap_paise)==(300,7500)
def test_premium_multiplier():
    q=calculate_cashback(10000,200,5000,"PREMIUM")
    assert (q.raw_cashback_paise,q.tier_monthly_cap_paise)==(400,10000)
def test_floor_not_round():
    assert calculate_cashback(333,200,5000,"BASIC").raw_cashback_paise==6
def test_zero_rate():
    assert calculate_cashback(10000,0,0,"BASIC").raw_cashback_paise==0
@pytest.mark.parametrize("tier",["INVALID","GOLD"])
def test_bad_tier(tier):
    with pytest.raises(ValueError): calculate_cashback(100,200,5000,tier)
def test_negative_input():
    with pytest.raises(ValueError): calculate_cashback(-1,200,5000,"BASIC")
