Banking DB Schema README

Summary:
- This repository file `Banking_db_schema.sql` contains a realistic MySQL schema for a banking management system
  including account types, beneficiaries, transactions, OTPs, loans, fixed deposits, cards, sessions, audit logs,
  recurring payments, fraud flags, account locks, stored procedures and sample queries.

Quick start:
1. Install MySQL 5.7+ / 8.x and ensure `mysql` CLI is available.
2. Run the schema file (from the workspace root):
```bash
mysql -u root -p < "c:/Users/Administrator/Desktop/DB Project/Banking_db_schema.sql"
```

Notes and usage:
- The schema creates `banking_db` and the required tables using InnoDB.
- Stored procedures included:
  - `sp_get_mini_statement(account_number, limit)` — returns recent transactions.
  - `sp_transfer(from_acc, to_acc, amount, otp_hash, remarks, OUT result)` — transfers with daily limit and OTP check.
  - `sp_freeze_account(account_number, locked_by, reason)` — freezes an account and logs an audit entry.

Security and production considerations:
- OTPs should be stored as secure hashes; the example uses `otp_hash` and you must perform hashing in application code.
- Card PANs and CVV must be handled according to PCI-DSS (store tokens, not raw PAN/CVV).
- Use prepared statements in your application layer and parameterized calls to procedures.
- Add encryption-at-rest for sensitive JSON fields if required.

Next steps you may want me to do:
- Add more stored procedures (loan origination, FD creation, recurring job runner).
- Add triggers to auto-create audit records for INSERT/UPDATE/DELETE.
- Integrate this schema with your `Banking_app.py` — I can create connectors and examples.
