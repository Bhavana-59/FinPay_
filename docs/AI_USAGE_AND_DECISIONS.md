# AI Assistance and Human Decisions

Update this document to reflect what your team actually inspected, changed, tested and accepted. Do not claim reviews or tests that were not performed.

## AI-assisted starter contributions
- Drafted layered FastAPI structure and relational entities.
- Drafted cashback logic, payment orchestration and reconciliation.
- Drafted API routes, tests, browser UI and documentation.

## Decisions requiring faculty/team confirmation
| Decision | Current implementation | Confirm because |
|---|---|---|
| Monthly cap scope | Per wallet, category and calendar month | Confirm grouping scope |
| Tier multipliers | Scale both rate and cap | Scenario says both are multiplied |
| Cashback credit | Credited immediately after payment | Confirm intended lifecycle |
| Top-up | Adds balance, zero cashback | Confirm top-up flow |
| Database | SQLite | Confirm required DBMS |
| Authentication | Separate JWT module with STUDENT/ADMIN roles | Align with TalentHub reuse/integration requirement |

## Human review checklist
- [ ] Compare rates and caps with official lab handout.
- [ ] Review ER diagram, keys, relationships and normalization.
- [ ] Run tests and add team-written test cases.
- [ ] Test duplicate requests, low balance and monthly boundaries.
- [ ] Review authorization and exposed data.
- [ ] Replace development secret and demo passwords before deployment.
- [ ] Record accepted, changed and rejected AI suggestions with reasons.

## Limitations
Educational simulation only: no bank/UPI/card integration, settlement, refunds, chargebacks, merchant onboarding, audit-grade rule versioning or production-grade concurrent payment locking. SQLite is for local demonstration, not high-volume deployment.
