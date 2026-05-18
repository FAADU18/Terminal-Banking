import os
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from hashlib import sha256

import jwt
from flask import Flask, g, jsonify, request
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bank_system.db")
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret")
JWT_ALGORITHM = "HS256"
JWT_EXP_HOURS = 12

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


def hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def generate_account_number() -> int:
    db = get_db()
    row = db.execute("SELECT COALESCE(MAX(account_number), 1000000000) AS max_acc FROM accounts").fetchone()
    return int(row["max_acc"]) + 1


def create_jwt(user_row: sqlite3.Row) -> str:
    payload = {
        "sub": user_row["id"],
        "email": user_row["email"],
        "name": user_row["name"],
        "account_number": user_row["account_number"],
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXP_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing bearer token"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        db = get_db()
        user = db.execute(
            "SELECT id, name, email, account_number FROM users WHERE id = ?",
            (decoded.get("sub"),),
        ).fetchone()
        if user is None:
            return jsonify({"message": "User not found"}), 401

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper


def init_db():
    db = sqlite3.connect(DB_PATH)

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            pin_hash TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            failed_login_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until TIMESTAMP,
            is_admin INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            account_number INTEGER NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_number) REFERENCES accounts(account_number)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL UNIQUE,
            sender_account INTEGER,
            receiver_account INTEGER,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_status TEXT NOT NULL DEFAULT 'SUCCESS',
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    db.commit()

    # Create a default demo account for quick testing.
    demo_email = "demo@bank.com"
    exists = db.execute("SELECT id FROM users WHERE email = ?", (demo_email,)).fetchone()
    if exists is None:
        demo_acc = db.execute(
            "SELECT account_number FROM accounts WHERE account_number = ?",
            (1000000001,),
        ).fetchone()
        if demo_acc is None:
            db.execute(
                """
                INSERT INTO accounts (account_number, name, pin_hash, balance)
                VALUES (?, ?, ?, ?)
                """,
                (1000000001, "Demo User", hash_password("1234"), 25000.0),
            )

        db.execute(
            """
            INSERT INTO users (name, email, password_hash, account_number)
            VALUES (?, ?, ?, ?)
            """,
            ("Demo User", demo_email, hash_password("password123"), 1000000001),
        )
        db.commit()

    db.close()


def user_public_payload(user_row: sqlite3.Row) -> dict:
    return {
        "id": user_row["id"],
        "name": user_row["name"],
        "email": user_row["email"],
        "account_number": user_row["account_number"],
    }


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/auth/register")
def register():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = (payload.get("password") or "").strip()

    if not name or not email or not password:
        return jsonify({"message": "name, email and password are required"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing is not None:
        return jsonify({"message": "Email already registered"}), 409

    account_number = generate_account_number()
    db.execute(
        """
        INSERT INTO accounts (account_number, name, pin_hash, balance)
        VALUES (?, ?, ?, ?)
        """,
        (account_number, name, hash_password("0000"), 0.0),
    )
    db.execute(
        """
        INSERT INTO users (name, email, password_hash, account_number)
        VALUES (?, ?, ?, ?)
        """,
        (name, email, hash_password(password), account_number),
    )
    db.commit()

    user = db.execute(
        "SELECT id, name, email, account_number FROM users WHERE email = ?",
        (email,),
    ).fetchone()

    return jsonify({"message": "Registration successful", "user": user_public_payload(user)}), 201


@app.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = (payload.get("password") or "").strip()

    if not email or not password:
        return jsonify({"message": "email and password are required"}), 400

    db = get_db()
    user = db.execute(
        "SELECT id, name, email, password_hash, account_number FROM users WHERE email = ?",
        (email,),
    ).fetchone()

    if user is None or user["password_hash"] != hash_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_jwt(user)
    return jsonify({"token": token, "user": user_public_payload(user)})


@app.get("/api/dashboard")
@auth_required
def dashboard():
    db = get_db()
    account_number = g.current_user["account_number"]

    account = db.execute(
        "SELECT balance FROM accounts WHERE account_number = ?",
        (account_number,),
    ).fetchone()

    credits = db.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE receiver_account = ?
        """,
        (account_number,),
    ).fetchone()["total"]

    debits = db.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE sender_account = ?
        """,
        (account_number,),
    ).fetchone()["total"]

    analytics_rows = db.execute(
        """
        WITH RECURSIVE dates(day) AS (
          SELECT DATE('now', '-6 days')
          UNION ALL
          SELECT DATE(day, '+1 day') FROM dates WHERE day < DATE('now')
        )
        SELECT
          d.day,
          COALESCE(SUM(CASE WHEN t.receiver_account = ? THEN t.amount ELSE 0 END), 0) AS credit,
          COALESCE(SUM(CASE WHEN t.sender_account = ? THEN t.amount ELSE 0 END), 0) AS debit
        FROM dates d
        LEFT JOIN transactions t ON DATE(t.created_at) = d.day
        GROUP BY d.day
        ORDER BY d.day
        """,
        (account_number, account_number),
    ).fetchall()

    analytics = [
        {
            "name": row["day"],
            "credit": round(float(row["credit"]), 2),
            "debit": round(float(row["debit"]), 2),
        }
        for row in analytics_rows
    ]

    notifications_rows = db.execute(
        """
        SELECT transaction_type, amount, created_at
        FROM transactions
        WHERE sender_account = ? OR receiver_account = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (account_number, account_number),
    ).fetchall()

    notifications = [
        {
            "id": idx + 1,
            "message": f"{row['transaction_type']} of ${float(row['amount']):.2f}",
            "time": row["created_at"],
        }
        for idx, row in enumerate(notifications_rows)
    ]

    return jsonify(
        {
            "stats": {
                "balance": round(float(account["balance"] if account else 0.0), 2),
                "credits": round(float(credits), 2),
                "debits": round(float(debits), 2),
            },
            "analytics": analytics,
            "notifications": notifications,
        }
    )


def create_transaction_id(prefix: str) -> str:
    return f"{prefix}-{int(datetime.utcnow().timestamp() * 1000)}"


@app.post("/api/transactions/deposit")
@auth_required
def deposit():
    payload = request.get_json(silent=True) or {}
    amount = float(payload.get("amount") or 0)

    if amount <= 0:
        return jsonify({"message": "Amount must be positive"}), 400

    db = get_db()
    account_number = g.current_user["account_number"]

    db.execute(
        "UPDATE accounts SET balance = balance + ? WHERE account_number = ?",
        (amount, account_number),
    )
    db.execute(
        """
        INSERT INTO transactions (transaction_id, sender_account, receiver_account, transaction_type, amount, transaction_status, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (create_transaction_id("DEP"), None, account_number, "DEPOSIT", amount, "SUCCESS", "Deposit"),
    )
    db.commit()

    return jsonify({"message": "Deposit successful"})


@app.post("/api/transactions/withdraw")
@auth_required
def withdraw():
    payload = request.get_json(silent=True) or {}
    amount = float(payload.get("amount") or 0)

    if amount <= 0:
        return jsonify({"message": "Amount must be positive"}), 400

    db = get_db()
    account_number = g.current_user["account_number"]

    row = db.execute("SELECT balance FROM accounts WHERE account_number = ?", (account_number,)).fetchone()
    balance = float(row["balance"] if row else 0.0)
    if amount > balance:
        return jsonify({"message": "Insufficient balance"}), 400

    db.execute(
        "UPDATE accounts SET balance = balance - ? WHERE account_number = ?",
        (amount, account_number),
    )
    db.execute(
        """
        INSERT INTO transactions (transaction_id, sender_account, receiver_account, transaction_type, amount, transaction_status, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (create_transaction_id("WDR"), account_number, None, "WITHDRAW", amount, "SUCCESS", "Withdraw"),
    )
    db.commit()

    return jsonify({"message": "Withdrawal successful"})


@app.post("/api/transactions/transfer")
@auth_required
def transfer():
    payload = request.get_json(silent=True) or {}
    to_account_raw = payload.get("to_account")
    remarks = (payload.get("remarks") or "Transfer").strip()

    try:
        to_account = int(to_account_raw)
    except (TypeError, ValueError):
        return jsonify({"message": "Invalid destination account number"}), 400

    amount = float(payload.get("amount") or 0)
    if amount <= 0:
        return jsonify({"message": "Amount must be positive"}), 400

    from_account = g.current_user["account_number"]
    if to_account == from_account:
        return jsonify({"message": "Cannot transfer to same account"}), 400

    db = get_db()
    sender = db.execute("SELECT balance FROM accounts WHERE account_number = ?", (from_account,)).fetchone()
    if sender is None:
        return jsonify({"message": "Sender account not found"}), 404

    sender_balance = float(sender["balance"])
    if amount > sender_balance:
        return jsonify({"message": "Insufficient balance"}), 400

    receiver = db.execute("SELECT account_number FROM accounts WHERE account_number = ?", (to_account,)).fetchone()

    db.execute("UPDATE accounts SET balance = balance - ? WHERE account_number = ?", (amount, from_account))
    if receiver is not None:
        db.execute("UPDATE accounts SET balance = balance + ? WHERE account_number = ?", (amount, to_account))

    db.execute(
        """
        INSERT INTO transactions (transaction_id, sender_account, receiver_account, transaction_type, amount, transaction_status, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (create_transaction_id("TRF"), from_account, to_account if receiver is not None else None, "TRANSFER", amount, "SUCCESS", remarks),
    )
    db.commit()

    return jsonify({"message": "Transfer successful"})


@app.get("/api/transactions/history")
@auth_required
def history():
    db = get_db()
    account_number = g.current_user["account_number"]

    rows = db.execute(
        """
        SELECT id, transaction_id, sender_account, receiver_account,
               transaction_type, amount, transaction_status, remarks, created_at
        FROM transactions
        WHERE sender_account = ? OR receiver_account = ?
        ORDER BY id DESC
        LIMIT 100
        """,
        (account_number, account_number),
    ).fetchall()

    transactions = [
        {
            "id": row["id"],
            "transaction_id": row["transaction_id"],
            "transaction_type": row["transaction_type"],
            "amount": float(row["amount"]),
            "transaction_status": row["transaction_status"],
            "remarks": row["remarks"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]

    return jsonify({"transactions": transactions})


@app.get("/api/transactions/mini-statement")
@auth_required
def mini_statement():
    db = get_db()
    account_number = g.current_user["account_number"]

    rows = db.execute(
        """
        SELECT id, transaction_id, transaction_type, amount, transaction_status, remarks, created_at
        FROM transactions
        WHERE sender_account = ? OR receiver_account = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (account_number, account_number),
    ).fetchall()

    transactions = [
        {
            "id": row["id"],
            "transaction_id": row["transaction_id"],
            "transaction_type": row["transaction_type"],
            "amount": float(row["amount"]),
            "transaction_status": row["transaction_status"],
            "remarks": row["remarks"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]

    return jsonify({"transactions": transactions})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
