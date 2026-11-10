# API Guide

Base URL: http://127.0.0.1:8000. Interactive docs: `/docs`.

| Method | Endpoint | Access |
|---|---|---|
| POST | `/api/auth/login` | Public |
| GET | `/api/wallet/me` | Student |
| GET | `/api/merchants` | Authenticated |
| POST | `/api/payments` | Student |
| POST | `/api/payments/top-up` | Student |
| GET | `/api/payments/history` | Student |
| GET | `/api/reconciliation/monthly?year=2026&month=11` | Admin |
| GET | `/health` | Public |

Login JSON:
```json
{"email":"rahul@finpay.local","password":"Student@123"}
```
Payment JSON:
```json
{"merchant_id":1,"amount_paise":10000,"idempotency_key":"canteen-demo-0001"}
```
Use a fresh idempotency key for every new payment. Reusing a key returns the original transaction result. Admin demo: `admin@finpay.local` / `Admin@123`. Use the returned JWT in Swagger's Authorize control.
