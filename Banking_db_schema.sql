-- Banking_db_schema.sql
-- Realistic MySQL schema for an enhanced Banking Management System
-- Charset and engine
CREATE DATABASE IF NOT EXISTS banking_db CHARACTER SET = 'utf8mb4' COLLATE = 'utf8mb4_unicode_ci';
USE banking_db;

-- Account types for flexibility
CREATE TABLE account_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(32) NOT NULL UNIQUE,
  name VARCHAR(64) NOT NULL,
  interest_rate DECIMAL(5,2) DEFAULT 0.00,
  min_balance DECIMAL(15,2) DEFAULT 0.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Customers / Users
CREATE TABLE customers (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100),
  email VARCHAR(255) UNIQUE,
  phone VARCHAR(32) UNIQUE,
  dob DATE,
  kyc_level ENUM('NONE','BASIC','FULL') DEFAULT 'NONE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Accounts
CREATE TABLE accounts (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  account_type_id INT NOT NULL,
  account_number VARCHAR(34) NOT NULL UNIQUE,
  currency VARCHAR(8) DEFAULT 'USD',
  balance DECIMAL(18,2) DEFAULT 0.00,
  status ENUM('ACTIVE','INACTIVE','FROZEN','CLOSED') DEFAULT 'ACTIVE',
  daily_transfer_limit DECIMAL(18,2) DEFAULT 1000.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX(idx_customer) (customer_id),
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
  FOREIGN KEY (account_type_id) REFERENCES account_types(id)
) ENGINE=InnoDB;

-- Beneficiaries (external or internal payees)
CREATE TABLE beneficiaries (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  account_id BIGINT NOT NULL,
  beneficiary_account_number VARCHAR(34) NOT NULL,
  beneficiary_name VARCHAR(200),
  beneficiary_bank VARCHAR(200),
  beneficiary_ifsc VARCHAR(32),
  verified TINYINT(1) DEFAULT 0,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Transactions (ledger-style)
CREATE TABLE transactions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  account_id BIGINT NOT NULL,
  related_account_number VARCHAR(34),
  beneficiary_id BIGINT,
  amount DECIMAL(18,2) NOT NULL,
  txn_type ENUM('DEPOSIT','WITHDRAWAL','TRANSFER','FEE','INTEREST','LOAN_PAYMENT','FD_CREATION') NOT NULL,
  status ENUM('PENDING','COMPLETED','FAILED','REVERSED') DEFAULT 'PENDING',
  remarks TEXT,
  reference VARCHAR(128),
  balance_after DECIMAL(18,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
  FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(id)
) ENGINE=InnoDB;

-- OTP / Verification table (general-purpose)
CREATE TABLE otps (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT,
  transaction_id BIGINT,
  otp_hash VARCHAR(255) NOT NULL,
  purpose ENUM('LOGIN','TRANSACTION','RESET','CONFIRM_BENEFICIARY') NOT NULL,
  expires_at DATETIME NOT NULL,
  used TINYINT(1) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
  FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Loans
CREATE TABLE loans (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  loan_account_id BIGINT,
  principal DECIMAL(18,2) NOT NULL,
  interest_rate DECIMAL(5,2) NOT NULL,
  term_months INT NOT NULL,
  outstanding_amount DECIMAL(18,2) NOT NULL,
  start_date DATE,
  end_date DATE,
  status ENUM('ACTIVE','CLOSED','DEFAULTED','SETTLED') DEFAULT 'ACTIVE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
) ENGINE=InnoDB;

-- Fixed deposits
CREATE TABLE fixed_deposits (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  account_id BIGINT NOT NULL,
  amount DECIMAL(18,2) NOT NULL,
  tenure_months INT NOT NULL,
  interest_rate DECIMAL(5,2) NOT NULL,
  start_date DATE NOT NULL,
  maturity_date DATE NOT NULL,
  status ENUM('ACTIVE','MATURED','CLOSED') DEFAULT 'ACTIVE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  FOREIGN KEY (account_id) REFERENCES accounts(id)
) ENGINE=InnoDB;

-- Notifications
CREATE TABLE notifications (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  type VARCHAR(64),
  channel ENUM('EMAIL','SMS','IN_APP') DEFAULT 'IN_APP',
  message TEXT,
  is_read TINYINT(1) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
) ENGINE=InnoDB;

-- Cards
CREATE TABLE cards (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  account_id BIGINT NOT NULL,
  card_number CHAR(16) NOT NULL UNIQUE,
  card_type ENUM('DEBIT','CREDIT') NOT NULL,
  expiry DATE NOT NULL,
  status ENUM('ACTIVE','BLOCKED','EXPIRED') DEFAULT 'ACTIVE',
  daily_withdrawal_limit DECIMAL(18,2) DEFAULT 500.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  FOREIGN KEY (account_id) REFERENCES accounts(id)
) ENGINE=InnoDB;

-- Sessions
CREATE TABLE sessions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  session_token VARCHAR(255) NOT NULL UNIQUE,
  ip_address VARCHAR(64),
  user_agent VARCHAR(512),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_active TIMESTAMP NULL,
  expires_at TIMESTAMP NULL,
  revoked TINYINT(1) DEFAULT 0,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
) ENGINE=InnoDB;

-- Audit logs
CREATE TABLE audit_logs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT,
  action VARCHAR(128) NOT NULL,
  object_type VARCHAR(64),
  object_id VARCHAR(128),
  old_value JSON,
  new_value JSON,
  source VARCHAR(64),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Recurring payments
CREATE TABLE recurring_payments (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  account_id BIGINT NOT NULL,
  beneficiary_id BIGINT NOT NULL,
  amount DECIMAL(18,2) NOT NULL,
  frequency ENUM('DAILY','WEEKLY','MONTHLY','YEARLY') NOT NULL,
  next_run DATE,
  status ENUM('ACTIVE','PAUSED','CANCELLED') DEFAULT 'ACTIVE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (account_id) REFERENCES accounts(id),
  FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(id)
) ENGINE=InnoDB;

-- Fraud detection / flags
CREATE TABLE fraud_flags (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  account_id BIGINT,
  transaction_id BIGINT,
  flag_type VARCHAR(64),
  score DECIMAL(5,2),
  details JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (account_id) REFERENCES accounts(id),
  FOREIGN KEY (transaction_id) REFERENCES transactions(id)
) ENGINE=InnoDB;

-- Account locks / freezes
CREATE TABLE account_locks (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  account_id BIGINT NOT NULL,
  locked_by VARCHAR(128),
  reason TEXT,
  locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NULL,
  active TINYINT(1) DEFAULT 1,
  FOREIGN KEY (account_id) REFERENCES accounts(id)
) ENGINE=InnoDB;

-- Indexes to speed common queries
CREATE INDEX idx_txn_account_created ON transactions(account_id, created_at);
CREATE INDEX idx_accounts_number ON accounts(account_number);

-- View: mini statement (last N transactions can be obtained using a procedure)
CREATE VIEW account_balances AS
SELECT a.id AS account_id, a.account_number, a.balance, a.status, c.first_name, c.last_name
FROM accounts a JOIN customers c ON a.customer_id = c.id;

-- Stored Procedures / Functions
DELIMITER $$
CREATE PROCEDURE sp_get_mini_statement(
  IN p_account_number VARCHAR(34),
  IN p_limit INT)
BEGIN
  SELECT t.id, t.txn_type, t.amount, t.status, t.remarks, t.reference, t.created_at
  FROM transactions t
  JOIN accounts a ON t.account_id = a.id
  WHERE a.account_number = p_account_number
  ORDER BY t.created_at DESC
  LIMIT p_limit;
END$$

-- Transfer procedure with daily limit and OTP validation
CREATE PROCEDURE sp_transfer(
  IN p_from_acc VARCHAR(34),
  IN p_to_acc VARCHAR(34),
  IN p_amount DECIMAL(18,2),
  IN p_otp_hash VARCHAR(255),
  IN p_remarks TEXT,
  OUT p_result VARCHAR(255)
)
BEGIN
  DECLARE v_from_id BIGINT;
  DECLARE v_to_id BIGINT;
  DECLARE v_balance DECIMAL(18,2);
  DECLARE v_limit DECIMAL(18,2);
  DECLARE v_today_total DECIMAL(18,2);
  DECLARE v_cust_id BIGINT;
  DECLARE v_ok TINYINT DEFAULT 1;

  START TRANSACTION;

  SELECT id, balance, customer_id, daily_transfer_limit INTO v_from_id, v_balance, v_cust_id, v_limit
  FROM accounts WHERE account_number = p_from_acc FOR UPDATE;

  IF v_from_id IS NULL THEN
    SET p_result = 'FROM_ACCOUNT_NOT_FOUND';
    SET v_ok = 0;
  ELSEIF v_balance < p_amount THEN
    SET p_result = 'INSUFFICIENT_FUNDS';
    SET v_ok = 0;
  ELSE
    SELECT COALESCE(SUM(amount),0) INTO v_today_total
    FROM transactions t JOIN accounts a ON t.account_id = a.id
    WHERE a.account_number = p_from_acc
      AND t.txn_type = 'TRANSFER'
      AND DATE(t.created_at) = CURDATE();

    IF (v_today_total + p_amount) > v_limit THEN
      SET p_result = 'DAILY_LIMIT_EXCEEDED';
      SET v_ok = 0;
    END IF;
  END IF;

  IF v_ok = 1 THEN
    IF NOT EXISTS (SELECT 1 FROM otps o WHERE o.customer_id = v_cust_id AND o.otp_hash = p_otp_hash AND o.purpose = 'TRANSACTION' AND o.used = 0 AND o.expires_at > NOW()) THEN
      SET p_result = 'OTP_INVALID_OR_EXPIRED';
      SET v_ok = 0;
    END IF;
  END IF;

  IF v_ok = 1 THEN
    SELECT id INTO v_to_id FROM accounts WHERE account_number = p_to_acc FOR UPDATE;
    -- Debit from source
    UPDATE accounts SET balance = balance - p_amount WHERE id = v_from_id;
    -- Credit to destination if internal
    IF v_to_id IS NOT NULL THEN
      UPDATE accounts SET balance = balance + p_amount WHERE id = v_to_id;
    END IF;

    -- Insert transaction records
    INSERT INTO transactions(account_id, related_account_number, beneficiary_id, amount, txn_type, status, remarks, reference, balance_after)
    VALUES (v_from_id, p_to_acc, NULL, p_amount, 'TRANSFER', 'COMPLETED', p_remarks, CONCAT('TRF-',UNIX_TIMESTAMP()), (SELECT balance FROM accounts WHERE id = v_from_id));

    IF v_to_id IS NOT NULL THEN
      INSERT INTO transactions(account_id, related_account_number, beneficiary_id, amount, txn_type, status, remarks, reference, balance_after)
      VALUES (v_to_id, p_from_acc, NULL, p_amount, 'TRANSFER', 'COMPLETED', p_remarks, CONCAT('TRF-',UNIX_TIMESTAMP()), (SELECT balance FROM accounts WHERE id = v_to_id));
    END IF;

    -- Mark OTP used
    UPDATE otps SET used = 1 WHERE customer_id = v_cust_id AND otp_hash = p_otp_hash AND purpose = 'TRANSACTION';

    -- Audit
    INSERT INTO audit_logs(user_id, action, object_type, object_id, new_value, source)
    VALUES (v_cust_id, 'TRANSFER', 'accounts', p_from_acc, JSON_OBJECT('to', p_to_acc, 'amount', p_amount, 'remarks', p_remarks), 'sp_transfer');

    COMMIT;
    SET p_result = 'OK';
  ELSE
    ROLLBACK;
  END IF;

  SELECT p_result;
END$$

-- Procedure to freeze account and create audit log
CREATE PROCEDURE sp_freeze_account(IN p_account_number VARCHAR(34), IN p_locked_by VARCHAR(128), IN p_reason TEXT)
BEGIN
  DECLARE v_acc_id BIGINT;
  SELECT id INTO v_acc_id FROM accounts WHERE account_number = p_account_number;
  IF v_acc_id IS NULL THEN
    SELECT 'ACCOUNT_NOT_FOUND' AS result;
  ELSE
    UPDATE accounts SET status = 'FROZEN' WHERE id = v_acc_id;
    INSERT INTO account_locks(account_id, locked_by, reason) VALUES (v_acc_id, p_locked_by, p_reason);
    INSERT INTO audit_logs(user_id, action, object_type, object_id, new_value, source) VALUES (NULL, 'FREEZE_ACCOUNT', 'accounts', p_account_number, JSON_OBJECT('locked_by', p_locked_by, 'reason', p_reason), 'sp_freeze_account');
    SELECT 'OK' AS result;
  END IF;
END$$

DELIMITER ;

-- Sample Queries
-- 1. Create basic account types
INSERT INTO account_types(code, name, interest_rate, min_balance) VALUES ('SAVINGS','Savings Account',1.25,100.00),('CURRENT','Current Account',0.00,0.00),('FD','Fixed Deposit',5.00,0.00);

-- 2. Create a customer and account (example)
-- INSERT INTO customers(first_name,last_name,email,phone) VALUES('Alice','Smith','alice@example.com','+15551234567');
-- Use the returned customer id to create an account in `accounts`.

-- 3. Get mini statement (last 10)
-- CALL sp_get_mini_statement('1234567890', 10);

-- 4. Make a transfer (example)
-- CALL sp_transfer('ACC123','EXT999',100.00,'<otp_hash>','Rent payment', @res); SELECT @res;
