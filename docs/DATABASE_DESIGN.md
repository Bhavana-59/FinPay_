# Database Design

## Entities
- **User:** login identity, email, password hash and role.
- **Wallet:** one wallet per student; balance in paise and tier.
- **Merchant:** merchant name, category and active status.
- **CashbackRule:** one cashback rate and monthly cap per category.
- **Transaction:** payment/top-up record, amount, cashback, idempotency key, status and timestamp.

## ER diagram
```mermaid
erDiagram
 USER ||--o| WALLET : owns
 WALLET ||--o{ TRANSACTION : records
 MERCHANT ||--o{ TRANSACTION : receives
 USER { int id PK string name string email UK string role }
 WALLET { int id PK int student_id FK,UK int balance_paise string tier }
 MERCHANT { int id PK string name UK string category }
 CASHBACK_RULE { int id PK string category UK int rate_basis_points int monthly_cap_paise }
 TRANSACTION { int id PK int wallet_id FK int merchant_id FK string transaction_type int amount_paise int cashback_paise string idempotency_key UK datetime created_at }
```
CashbackRule is matched through the category. A rule-version foreign key is a possible future extension for audit history.

## Keys, relationships and normalization
- Wallet.student_id is a unique foreign key to User.
- Transaction.wallet_id references Wallet.
- Transaction.merchant_id references Merchant and is nullable for top-ups.
- Transaction.idempotency_key is unique.
- User, wallet, merchant and cashback rule facts are stored separately, avoiding repeated merchant/user details in transaction rows.
- The schema is broadly normalized for this MVP. Transaction retains the category used at payment time for historical reporting.

## Money
₹125.50 is stored as 12550 paise. Integer storage avoids binary floating-point rounding errors.
