# FinPay – Campus Digital Wallet and Cashback System

FinPay is an educational campus-wallet application. It demonstrates how a student can view a wallet balance, add simulated funds, pay campus merchants, and see cashback earned on eligible payments. Cashback is calculated by merchant category, wallet tier, and monthly category cap.


## Technology stack

- **Frontend:** React 18, Vite 5, JavaScript, Tailwind CSS 4/PostCSS
- **Backend:** Python 3.10+, FastAPI, Pydantic 2, SQLAlchemy 2, Uvicorn
- **Database:** SQLite 
- **Authentication:** JWT bearer tokens with `python-jose`; passwords are stored as PBKDF2 hashes
- **Tests:** pytest and FastAPI/httpx test tooling



### Terminal 1: start the backend

Run these commands from the project root:

```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r .\backend\requirements.txt
if (-not (Test-Path .\backend\.env)) {
    Copy-Item .\backend\.env.example .\backend\.env
}
Set-Location .\backend
python -m uvicorn main:app --reload
```

 `http://127.0.0.1:8000`.

### Terminal 2: start the frontend

Open a second terminal at the project root:

```powershell
Set-Location .\frontend
npm install
npm run dev
```

Open **http://localhost:5173**. Vite forwards `/api` and `/health` requests to the backend at `http://127.0.0.1:8000`; start the backend before using the dashboard.

### Local URLs

| Purpose | URL |
|---|---|
| Student frontend | [http://localhost:5173](http://localhost:5173) |
| Backend API base | [http://127.0.0.1:8000](http://127.0.0.1:8000) |
| Swagger UI | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| OpenAPI schema | [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json) |
| Health check | [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) |

## Demo accounts

These accounts are created by `backend/app/services/seed_service.py` on a fresh database. 
| Name | Email | Password | Role | Wallet tier | Initial balance |
|---|---|---|---|---|---:|
| Rahul | `rahul@finpay.local` | `Student@123` | Student | BASIC | ₹1,000.00 |
| Ananya | `ananya@finpay.local` | `Student@123` | Student | PRIME | ₹2,500.00 |
| FinPay Admin | `admin@finpay.local` | `Admin@123` | Admin | No wallet | — |

The web dashboard is student-only. The admin account can access the admin-protected monthly reconciliation API, but the project does not provide an admin dashboard.

## Features and functionality

### Student wallet

- Student login with email and password; authenticated API calls use a JWT bearer token.
- Wallet balance and BASIC/PRIME tier display.
- Add simulated funds (top-up); top-ups do not earn cashback.
- Make payments to active campus merchants and view recent transactions, including cashback status.
- Current seeded merchants represent CANTEEN, STATIONERY, TRANSPORT, HOSTEL, and ONLINE categories.

### Cashback

Cashback is calculated with integer paise and floor division. Each category has a base cashback rate and a base monthly cap per wallet/category. The selected wallet tier multiplies **both** the rate and cap: BASIC = 1x, PRIME = 1.5x, and PREMIUM = 2x.

| Category | Seeded base rate | Seeded base monthly cap |
|---|---:|---:|
| CANTEEN | 2% | ₹50 |
| STATIONERY | 1% | ₹20 |
| TRANSPORT | 3% | ₹100 |
| HOSTEL | 0.5% | ₹200 |
| ONLINE | 1% | ₹30 |

For example, the PRIME tier applies a 1.5x multiplier to both a category's base rate and its cap. Cashback is limited by the remaining monthly category cap. The transaction history shows the reason recorded when each payment was processed:

- **Cashback earned** — the full calculated cashback was awarded.
- **Monthly cap limit reached** — some cashback was awarded, but the remaining cap limited the amount.
- **Monthly limit exhausted** — the monthly cap was already exhausted, so no cashback was awarded.
- **No cashback for this amount** — the calculated cashback rounded down to zero.
- **Not applicable** — the transaction was a top-up.

### Duplicate payment protection

Payment and top-up requests require an idempotency key (8–100 characters). A key is unique across transactions. Repeating a key for the same student returns the original transaction instead of processing it again. Reusing the key for another student's transaction returns HTTP 409. The service treats a same-student key as a replay even if the request amount or merchant differs; use a new key for every new intended payment.

## Suggested walkthrough

1. Start the backend and frontend using the two terminals above.
2. Sign in to the dashboard as `rahul@finpay.local` using `Student@123`.
3. Check the displayed BASIC tier and wallet balance.
4. Optionally add a small amount of simulated funds. Top-ups appear in history with cashback status **Not applicable**.
5. Make a modest payment to a merchant. The payment form accepts rupees; the API stores amounts in paise.
6. Make payments to merchants from different categories to see their seeded rates applied. Cashback status and monthly caps are tracked per wallet and category.
7. Review Recent Transactions for the cashback amount and the recorded Cashback Status. A sufficiently small purchase can round down to zero cashback.
8. For an idempotency demonstration, use the API example below. The first call creates a simulated payment; the second call repeats the same key and should return the same transaction with `"replayed": true`.

## Architecture and workflow

```text
FinPay/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routers and HTTP endpoints
│   │   ├── core/          # Configuration, JWT security, DB engine/session
│   │   ├── models/        # SQLAlchemy entities and constraints
│   │   ├── repositories/  # Queries for users, wallets, merchants, cashback, transactions
│   │   ├── schemas/       # Pydantic request/response validation
│   │   ├── services/      # Auth, wallet, merchant, payment, cashback, seed, reconciliation
│   │   └── main.py        # FastAPI app, startup initialization, router registration
│   ├── main.py            # Uvicorn entry point (imports app.main:app)
│   ├── requirements.txt
│   ├── .env.example
│   └── finpay.db          # Created at runtime by SQLite; not required in a fresh checkout
├── frontend/
│   ├── src/
│   │   ├── components/    # Header and notice
│   │   ├── pages/         # Login and student dashboard
│   │   ├── api.js         # Shared fetch helper
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js     # Dev server and backend proxy
└── docs/                  # API, architecture, algorithm, and database documentation
```

### API endpoints

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| `GET` | `/health` | Public | Backend health response |
| `POST` | `/api/auth/login` | Public | Login with a JSON email/password body |
| `GET` | `/api/wallet/me` | Student | Current wallet balance and tier |
| `GET` | `/api/merchants` | Authenticated | List active merchants |
| `POST` | `/api/payments` | Student | Make a payment |
| `POST` | `/api/payments/top-up` | Student | Add wallet funds |
| `GET` | `/api/payments/history` | Student | Recent wallet transactions |
| `GET` | `/api/reconciliation/monthly` | Admin | Monthly transaction summary |




## task  information and technologies

- **task name:** FinPay – Campus Digital Wallet and Cashback System
- **Purpose:** Educational simulation of campus wallet payments and category-based cashback
- **Frontend:** React, Vite, Tailwind CSS/PostCSS
- **Backend:** FastAPI, Pydantic, SQLAlchemy, Uvicorn
- **Persistence:** SQLite by default; `DATABASE_URL` can be configured in `backend/.env`
- **Authentication:** JWT bearer authentication; password hashing with PBKDF2-HMAC-SHA256
- **API reference:** [docs/API_GUIDE.md](docs/API_GUIDE.md)
- **Architecture overview:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Algorithm notes:** [docs/ALGORITHM_DESIGN.md](docs/ALGORITHM_DESIGN.md)
- **Database design:** [docs/DATABASE_DESIGN.md](docs/DATABASE_DESIGN.md)

