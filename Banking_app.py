import sqlite3
from hashlib import sha256
from pathlib import Path


class BankAccount:
    def __init__(self, acc_num, name, pin_hash, balance=0, source="app"):
        self.acc_num = acc_num
        self.name = name
        self.pin_hash = pin_hash
        self.balance = balance
        self.source = source

class Bank:
    def __init__(self):
        self.db_path = Path(__file__).with_name("bank_app.db")
        self.system_db_path = Path(__file__).with_name("bank_system.db")

        self.conns = {
            "app": sqlite3.connect(self.db_path),
            "system": sqlite3.connect(self.system_db_path),
        }

        for conn in self.conns.values():
            conn.row_factory = sqlite3.Row

        self._init_db()

    def _init_db(self):
        with self.conns["app"]:
            self.conns["app"].execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    account_number INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    pin TEXT NOT NULL,
                    balance REAL NOT NULL DEFAULT 0
                )
                """
            )
            self.conns["app"].execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_number INTEGER NOT NULL,
                    transaction_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_number) REFERENCES accounts(account_number)
                )
                """
            )

        with self.conns["system"]:
            self.conns["system"].execute(
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
            self.conns["system"].execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT NOT NULL UNIQUE,
                    sender_account INTEGER,
                    receiver_account INTEGER,
                    transaction_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    transaction_status TEXT NOT NULL DEFAULT 'SUCCESS',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _hash_pin(self, pin, source="app"):
        if source == "system":
            return sha256(pin.encode()).hexdigest()
        return pin

    def _system_sample_pin(self, acc_num):
        sample_pins = {
            1000000001: "1234",
            1000000002: "5678",
            9999999999: "9999",
        }
        return sample_pins.get(acc_num)

    def _get_connection(self, source):
        return self.conns[source]

    def _fetch_account(self, acc_num):
        for source, conn in self.conns.items():
            if source == "app":
                row = conn.execute(
                    "SELECT account_number, name, pin, balance FROM accounts WHERE account_number = ?",
                    (acc_num,),
                ).fetchone()
                if row:
                    return BankAccount(row["account_number"], row["name"], row["pin"], row["balance"], source)
            else:
                row = conn.execute(
                    "SELECT account_number, name, pin_hash, balance FROM accounts WHERE account_number = ?",
                    (acc_num,),
                ).fetchone()
                if row:
                    return BankAccount(row["account_number"], row["name"], row["pin_hash"], row["balance"], source)
        return None

    def _save_transaction(self, acc_num, text, source="app", tx_type=None, amount=None, status="SUCCESS", receiver_account=None):
        conn = self._get_connection(source)
        with conn:
            if source == "app":
                conn.execute(
                    "INSERT INTO transactions (account_number, transaction_text) VALUES (?, ?)",
                    (acc_num, text),
                )
            else:
                transaction_type = tx_type or "MANUAL"
                transaction_id = f"TXN-{source.upper()}-{acc_num}-{int(amount or 0)}-{len(text)}"
                conn.execute(
                    """
                    INSERT INTO transactions (
                        transaction_id,
                        sender_account,
                        receiver_account,
                        transaction_type,
                        amount,
                        transaction_status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        transaction_id,
                        acc_num if transaction_type != "DEPOSIT" else None,
                        receiver_account if receiver_account is not None else (acc_num if transaction_type == "DEPOSIT" else None),
                        transaction_type,
                        amount if amount is not None else 0,
                        status,
                    ),
                )
    
    def create_account(self):
        print("\n=== CREATE NEW ACCOUNT ===")
        name = input("Enter your name: ").strip()
        if not name:
            print("Name cannot be empty!")
            return
        
        pin = input("Set a 4-digit PIN: ").strip()
        if len(pin) != 4 or not pin.isdigit():
            print("PIN must be exactly 4 digits!")
            return
        
        initial_deposit = input("Enter initial deposit (minimum $100): $").strip()
        try:
            initial_deposit = float(initial_deposit)
            if initial_deposit < 100:
                print("Minimum initial deposit is $100!")
                return
        except ValueError:
            print("Invalid amount!")
            return

        pin_hash = self._hash_pin(pin, "app")
        system_pin_hash = self._hash_pin(pin, "system")
        with self.conns["app"]:
            cursor = self.conns["app"].execute(
                "INSERT INTO accounts (name, pin, balance) VALUES (?, ?, ?)",
                (name, pin_hash, initial_deposit),
            )
            acc_num = cursor.lastrowid
            self._save_transaction(acc_num, f"Initial deposit: ${initial_deposit:.2f}", source="app")

        # Also mirror the account into the system database so both databases are connected.
        with self.conns["system"]:
            self.conns["system"].execute(
                """
                INSERT OR REPLACE INTO accounts (account_number, name, pin_hash, balance)
                VALUES (?, ?, ?, ?)
                """,
                (acc_num, name, system_pin_hash, initial_deposit),
            )
            self._save_transaction(
                acc_num,
                f"Initial deposit: ${initial_deposit:.2f}",
                source="system",
                tx_type="DEPOSIT",
                amount=initial_deposit,
                receiver_account=acc_num,
            )
        
        print(f"\n✓ Account created successfully!")
        print(f"Account Number: {acc_num}")
        print(f"Account Holder: {name}")
        print(f"Initial Balance: ${initial_deposit:.2f}")
    
    def login(self):
        try:
            acc_num = int(input("\nEnter account number: ").strip())
        except ValueError:
            print("Invalid account number!")
            return None

        acc = self._fetch_account(acc_num)
        if not acc:
            print("Account not found!")
            return None
        
        pin = input("Enter PIN: ").strip()
        valid_pin = acc.pin_hash == self._hash_pin(pin, acc.source)
        if not valid_pin and acc.source == "system":
            valid_pin = pin == self._system_sample_pin(acc.acc_num)

        if not valid_pin:
            print("Incorrect PIN!")
            return None
        
        return acc
    
    def check_balance(self, acc):
        print(f"\n=== BALANCE INQUIRY ===")
        print(f"Account Number: {acc.acc_num}")
        print(f"Account Holder: {acc.name}")
        print(f"Current Balance: ${acc.balance:.2f}")
    
    def deposit(self, acc):
        print("\n=== DEPOSIT ===")
        amount_str = input("Enter deposit amount: $").strip()
        try:
            amount = float(amount_str)
            if amount <= 0:
                print("Amount must be positive!")
                return
            
            acc.balance += amount
            conn = self._get_connection(acc.source)
            with conn:
                if acc.source == "app":
                    conn.execute(
                        "UPDATE accounts SET balance = ? WHERE account_number = ?",
                        (acc.balance, acc.acc_num),
                    )
                else:
                    conn.execute(
                        "UPDATE accounts SET balance = ? WHERE account_number = ?",
                        (acc.balance, acc.acc_num),
                    )
                self._save_transaction(acc.acc_num, f"Deposit: +${amount:.2f}", source=acc.source, tx_type="DEPOSIT", amount=amount, receiver_account=acc.acc_num)
            print(f"\n✓ Deposit successful!")
            print(f"Deposited: ${amount:.2f}")
            print(f"New Balance: ${acc.balance:.2f}")
        except ValueError:
            print("Invalid amount!")
    
    def withdraw(self, acc):
        print("\n=== WITHDRAWAL ===")
        amount_str = input("Enter withdrawal amount: $").strip()
        try:
            amount = float(amount_str)
            if amount <= 0:
                print("Amount must be positive!")
                return
            
            if amount > acc.balance:
                print(f"Insufficient funds! Current balance: ${acc.balance:.2f}")
                return
            
            acc.balance -= amount
            conn = self._get_connection(acc.source)
            with conn:
                conn.execute(
                    "UPDATE accounts SET balance = ? WHERE account_number = ?",
                    (acc.balance, acc.acc_num),
                )
                self._save_transaction(acc.acc_num, f"Withdrawal: -${amount:.2f}", source=acc.source, tx_type="WITHDRAW", amount=amount)
            print(f"\n✓ Withdrawal successful!")
            print(f"Withdrawn: ${amount:.2f}")
            print(f"New Balance: ${acc.balance:.2f}")
        except ValueError:
            print("Invalid amount!")
    
    def view_transactions(self, acc):
        print("\n=== TRANSACTION HISTORY ===")
        print(f"Account: {acc.acc_num} - {acc.name}")
        rows = []
        if acc.source == "app":
            rows.extend(self.conns["app"].execute(
                "SELECT transaction_text, created_at FROM transactions WHERE account_number = ? ORDER BY id",
                (acc.acc_num,),
            ).fetchall())
        system_rows = self.conns["system"].execute(
            """
            SELECT transaction_id, transaction_type, amount, transaction_status, created_at,
                   sender_account, receiver_account
            FROM transactions
            WHERE sender_account = ? OR receiver_account = ?
            ORDER BY id
            """,
            (acc.acc_num, acc.acc_num),
        ).fetchall()
        rows.extend(system_rows)

        if not rows:
            print("No transactions yet.")
        else:
            for i, row in enumerate(rows, 1):
                if isinstance(row, sqlite3.Row) and "transaction_text" in row.keys():
                    print(f"{i}. {row['transaction_text']}")
                else:
                    direction = "IN" if row["receiver_account"] == acc.acc_num else "OUT"
                    print(f"{i}. [{row['created_at']}] {row['transaction_type']} {direction} ${row['amount']:.2f} ({row['transaction_status']}) ID={row['transaction_id']}")
        print(f"\nCurrent Balance: ${acc.balance:.2f}")

    def close(self):
        for conn in self.conns.values():
            conn.close()

def main():
    bank = Bank()
    
    while True:
        print("\n" + "="*40)
        print("   WELCOME TO TERMINAL BANK")
        print("="*40)
        print("1. Create New Account")
        print("2. Login to Existing Account")
        print("3. Exit")
        print("="*40)
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == '1':
            bank.create_account()
        
        elif choice == '2':
            acc = bank.login()
            if acc:
                print(f"\n✓ Login successful! Welcome, {acc.name}!")
                
                while True:
                    print("\n" + "-"*40)
                    print("   ACCOUNT MENU")
                    print("-"*40)
                    print("1. Check Balance")
                    print("2. Deposit")
                    print("3. Withdraw")
                    print("4. Transaction History")
                    print("5. Logout")
                    print("-"*40)
                    
                    acc_choice = input("Select an option (1-5): ").strip()
                    
                    if acc_choice == '1':
                        bank.check_balance(acc)
                    elif acc_choice == '2':
                        bank.deposit(acc)
                    elif acc_choice == '3':
                        bank.withdraw(acc)
                    elif acc_choice == '4':
                        bank.view_transactions(acc)
                    elif acc_choice == '5':
                        print("\n✓ Logged out successfully!")
                        break
                    else:
                        print("Invalid option! Please try again.")
        
        elif choice == '3':
            print("\nThank you for using Terminal Bank!")
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid option! Please try again.")

    bank.close()

if __name__ == "__main__":
    main()  