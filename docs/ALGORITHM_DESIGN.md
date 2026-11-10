# Algorithm Design

## Cashback calculation
100 basis points = 1%. The scenario rates are stored as basis points: 2% = 200.

Tier multipliers: BASIC 1x, PRIME 1.5x, PREMIUM 2x. Both rate and cap are scaled.

```text
FUNCTION calculate_cashback(amount, rate_bps, base_cap, tier):
    validate non-negative inputs and valid tier
    (numerator, denominator) = tier_multiplier[tier]
    raw = FLOOR(amount * rate_bps * numerator / (10000 * denominator))
    tier_cap = FLOOR(base_cap * numerator / denominator)
    RETURN raw, tier_cap
END
```

## Payment orchestration
```text
FUNCTION process_payment(student, merchant, amount, idempotency_key):
    if key exists: return original result (or reject if another wallet owns it)
    find wallet and active merchant
    validate positive amount and sufficient balance
    find category cashback rule
    raw, tier_cap = calculate_cashback(...)
    earned = sum this wallet's successful cashback in this category this month
    remaining = MAX(0, tier_cap - earned)
    awarded = MIN(raw, remaining)
    BEGIN DATABASE TRANSACTION
        wallet balance = balance - amount + awarded
        insert transaction
    COMMIT
    return result
END
```

## Complexity
- Cashback calculation: O(1) time and O(1) extra space.
- Indexed idempotency lookup: typically O(log n) in a B-tree index.
- Monthly cashback aggregation: depends on matching transaction rows; the wallet/category/time index helps.
- Reconciliation in this MVP reads the month's rows and aggregates them in memory: O(n) time and O(n) memory. SQL GROUP BY is a future optimization.

## Boundary tests
Below cap, exactly at cap, above cap, cap exhausted, floor not round, zero rate, invalid tier, negative inputs, repeated idempotency key and insufficient balance.
