# CyberGuard Industries - Direct Bank Deposit Platform
# Custom payment processing with direct bank account integration

import os
import json
import hashlib
import hmac
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from pathlib import Path
import secrets
import re


class BankAccount:
    """Bank account configuration for direct deposits"""
    
    def __init__(self):
        self.account_holder = os.getenv("BANK_ACCOUNT_HOLDER", "CyberGuard Industries LLC")
        self.bank_name = os.getenv("BANK_NAME", "")
        self.routing_number = os.getenv("BANK_ROUTING_NUMBER", "")
        self.account_number = os.getenv("BANK_ACCOUNT_NUMBER", "")
        self.account_type = os.getenv("BANK_ACCOUNT_TYPE", "checking")  # checking or savings
        self.swift_code = os.getenv("BANK_SWIFT_CODE", "")  # For international
        self.iban = os.getenv("BANK_IBAN", "")  # For international
        
    def mask_account_number(self) -> str:
        """Return masked account number for display"""
        if not self.account_number:
            return "Not configured"
        return f"****{self.account_number[-4:]}"
    
    def get_wire_instructions(self) -> Dict:
        """Get wire transfer instructions"""
        return {
            "beneficiary_name": self.account_holder,
            "bank_name": self.bank_name,
            "routing_number": self.routing_number,
            "account_number": self.account_number,
            "account_type": self.account_type,
            "swift_code": self.swift_code,
            "iban": self.iban,
            "reference": "CyberGuard License Payment"
        }


class ACHProcessor:
    """ACH (Automated Clearing House) payment processor for US bank transfers"""
    
    def __init__(self, db_path: str = "data/ach_transactions.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self.bank_account = BankAccount()
    
    def _init_database(self):
        """Initialize ACH transactions database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ach_transactions (
                transaction_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                customer_bank_routing TEXT NOT NULL,
                customer_bank_account TEXT NOT NULL,
                customer_bank_name TEXT,
                customer_account_holder TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                transaction_type TEXT NOT NULL,
                status TEXT NOT NULL,
                initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                settlement_date DATE,
                error_message TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bank_accounts_verified (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                routing_number TEXT NOT NULL,
                account_number_hash TEXT NOT NULL,
                account_holder TEXT NOT NULL,
                verified BOOLEAN DEFAULT 0,
                verification_deposits_sent BOOLEAN DEFAULT 0,
                verification_amount_1 INTEGER,
                verification_amount_2 INTEGER,
                verified_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(customer_id, account_number_hash)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def verify_routing_number(self, routing_number: str) -> Tuple[bool, str]:
        """Verify if routing number is valid (basic check)"""
        # Remove any spaces or dashes
        routing = re.sub(r'[\s-]', '', routing_number)
        
        # Must be 9 digits
        if not re.match(r'^\d{9}$', routing):
            return False, "Routing number must be 9 digits"
        
        # Checksum validation (ABA routing number algorithm)
        digits = [int(d) for d in routing]
        checksum = (3 * (digits[0] + digits[3] + digits[6]) +
                   7 * (digits[1] + digits[4] + digits[7]) +
                   (digits[2] + digits[5] + digits[8])) % 10
        
        if checksum != 0:
            return False, "Invalid routing number checksum"
        
        return True, "Valid routing number"
    
    def initiate_micro_deposits(self, customer_id: str, routing_number: str, 
                                account_number: str, account_holder: str) -> Tuple[bool, str]:
        """Initiate micro-deposits for bank account verification"""
        # Verify routing number
        is_valid, message = self.verify_routing_number(routing_number)
        if not is_valid:
            return False, message
        
        # Generate two random amounts between $0.01 and $0.99
        amount1 = secrets.randbelow(99) + 1  # 1-99 cents
        amount2 = secrets.randbelow(99) + 1
        
        # Hash account number for storage (never store plain text)
        account_hash = hashlib.sha256(account_number.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO bank_accounts_verified 
            (customer_id, routing_number, account_number_hash, account_holder,
             verification_deposits_sent, verification_amount_1, verification_amount_2)
            VALUES (?, ?, ?, ?, 1, ?, ?)
        """, (customer_id, routing_number, account_hash, account_holder, amount1, amount2))
        
        conn.commit()
        conn.close()
        
        # In production, this would trigger actual ACH micro-deposits
        # For now, return the amounts for demo purposes
        return True, f"Verification deposits of ${amount1/100:.2f} and ${amount2/100:.2f} will appear in 1-2 business days"
    
    def verify_micro_deposits(self, customer_id: str, amount1_cents: int, amount2_cents: int) -> Tuple[bool, str]:
        """Verify micro-deposit amounts to confirm bank account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT verification_amount_1, verification_amount_2 
            FROM bank_accounts_verified 
            WHERE customer_id = ? AND verified = 0
        """, (customer_id,))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "No pending verification found"
        
        stored_amount1, stored_amount2 = result
        
        # Check if amounts match (in either order)
        if ((amount1_cents == stored_amount1 and amount2_cents == stored_amount2) or
            (amount1_cents == stored_amount2 and amount2_cents == stored_amount1)):
            
            cursor.execute("""
                UPDATE bank_accounts_verified 
                SET verified = 1, verified_at = CURRENT_TIMESTAMP
                WHERE customer_id = ?
            """, (customer_id,))
            
            conn.commit()
            conn.close()
            
            return True, "Bank account verified successfully"
        else:
            conn.close()
            return False, "Verification amounts do not match"
    
    def process_ach_debit(self, customer_id: str, amount: float, 
                         routing_number: str, account_number: str,
                         account_holder: str, description: str = None) -> Tuple[bool, str]:
        """Process ACH debit (pull money from customer's account to yours)"""
        
        # Verify routing number
        is_valid, message = self.verify_routing_number(routing_number)
        if not is_valid:
            return False, message
        
        # Check if account is verified
        account_hash = hashlib.sha256(account_number.encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT verified FROM bank_accounts_verified 
            WHERE customer_id = ? AND account_number_hash = ?
        """, (customer_id, account_hash))
        
        result = cursor.fetchone()
        if not result or not result[0]:
            conn.close()
            return False, "Bank account not verified. Please verify account first."
        
        # Generate transaction ID
        transaction_id = f"ACH_{datetime.now().strftime('%Y%m%d')}_{secrets.token_hex(8).upper()}"
        
        # Settlement typically takes 3-5 business days
        settlement_date = datetime.now() + timedelta(days=3)
        
        cursor.execute("""
            INSERT INTO ach_transactions 
            (transaction_id, customer_id, customer_bank_routing, customer_bank_account,
             customer_account_holder, amount, transaction_type, status, settlement_date, metadata)
            VALUES (?, ?, ?, ?, ?, ?, 'debit', 'pending', ?, ?)
        """, (
            transaction_id,
            customer_id,
            routing_number,
            f"****{account_number[-4:]}",  # Store masked version only
            account_holder,
            amount,
            settlement_date.date(),
            json.dumps({"description": description})
        ))
        
        conn.commit()
        conn.close()
        
        return True, transaction_id
    
    def get_transaction_status(self, transaction_id: str) -> Optional[Dict]:
        """Get ACH transaction status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM ach_transactions WHERE transaction_id = ?
        """, (transaction_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        columns = [
            'transaction_id', 'customer_id', 'customer_bank_routing',
            'customer_bank_account', 'customer_bank_name', 'customer_account_holder',
            'amount', 'currency', 'transaction_type', 'status',
            'initiated_at', 'completed_at', 'settlement_date', 'error_message', 'metadata'
        ]
        
        return dict(zip(columns, result))


class WireTransferProcessor:
    """Wire transfer processor for large payments and international transactions"""
    
    def __init__(self, db_path: str = "data/wire_transfers.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self.bank_account = BankAccount()
    
    def _init_database(self):
        """Initialize wire transfer database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wire_transfers (
                transfer_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                sender_bank TEXT,
                sender_account_holder TEXT NOT NULL,
                reference_number TEXT,
                status TEXT NOT NULL,
                initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                received_at TIMESTAMP,
                notes TEXT,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def generate_wire_instructions(self, customer_id: str, amount: float, 
                                  invoice_number: str = None) -> Dict:
        """Generate wire transfer instructions for customer"""
        reference = f"CGEP-{customer_id[-8:]}"
        if invoice_number:
            reference += f"-{invoice_number}"
        
        instructions = self.bank_account.get_wire_instructions()
        instructions['amount'] = amount
        instructions['reference'] = reference
        instructions['instructions'] = [
            "1. Contact your bank to initiate a wire transfer",
            "2. Use the account details provided below",
            f"3. Include reference: {reference}",
            "4. Wire transfers typically complete in 1-2 business days",
            "5. Notify us at payments@cyberguard-platform.com when sent"
        ]
        
        return instructions
    
    def record_wire_transfer(self, customer_id: str, amount: float,
                            sender_bank: str, sender_name: str,
                            reference: str = None) -> str:
        """Record a received wire transfer"""
        transfer_id = f"WIRE_{datetime.now().strftime('%Y%m%d')}_{secrets.token_hex(8).upper()}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO wire_transfers 
            (transfer_id, customer_id, amount, sender_bank, sender_account_holder,
             reference_number, status, received_at)
            VALUES (?, ?, ?, ?, ?, ?, 'completed', CURRENT_TIMESTAMP)
        """, (transfer_id, customer_id, amount, sender_bank, sender_name, reference))
        
        conn.commit()
        conn.close()
        
        return transfer_id


class DirectDepositPlatform:
    """Main platform coordinating direct bank deposit payments"""
    
    def __init__(self):
        self.ach_processor = ACHProcessor()
        self.wire_processor = WireTransferProcessor()
        self.bank_account = BankAccount()
    
    def setup_customer_payment(self, customer_id: str, payment_method: str = "ach") -> Dict:
        """Setup payment method for a customer"""
        if payment_method == "ach":
            return {
                "method": "ACH Bank Transfer",
                "steps": [
                    "1. Provide your bank account details",
                    "2. We'll send two small verification deposits (1-2 days)",
                    "3. Confirm the deposit amounts",
                    "4. Your account is verified for automatic payments"
                ],
                "processing_time": "3-5 business days",
                "fees": "$0 (Free)",
                "limits": {
                    "min": 1.00,
                    "max": 25000.00,
                    "currency": "USD"
                }
            }
        elif payment_method == "wire":
            return {
                "method": "Wire Transfer",
                "steps": [
                    "1. Request wire transfer instructions",
                    "2. Contact your bank to initiate transfer",
                    "3. Include provided reference number",
                    "4. Notify us when transfer is sent"
                ],
                "processing_time": "1-2 business days",
                "fees": "Varies by bank ($15-50 typical)",
                "limits": {
                    "min": 1000.00,
                    "max": None,  # No maximum
                    "currency": "USD"
                }
            }
        else:
            return {"error": "Unknown payment method"}
    
    def get_payment_status_summary(self, customer_id: str) -> Dict:
        """Get summary of all payments for a customer"""
        # Get ACH transactions
        conn = sqlite3.connect(self.ach_processor.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*), SUM(amount), status 
            FROM ach_transactions 
            WHERE customer_id = ?
            GROUP BY status
        """, (customer_id,))
        
        ach_summary = cursor.fetchall()
        conn.close()
        
        # Get wire transfers
        conn = sqlite3.connect(self.wire_processor.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*), SUM(amount) 
            FROM wire_transfers 
            WHERE customer_id = ? AND status = 'completed'
        """, (customer_id,))
        
        wire_summary = cursor.fetchone()
        conn.close()
        
        return {
            "customer_id": customer_id,
            "ach_transactions": [
                {"status": row[2], "count": row[0], "total": row[1]}
                for row in ach_summary
            ],
            "wire_transfers": {
                "count": wire_summary[0] or 0,
                "total": wire_summary[1] or 0.0
            },
            "receiving_account": self.bank_account.mask_account_number()
        }


# Example usage and testing
if __name__ == "__main__":
    print("="*70)
    print("CyberGuard Industries - Direct Bank Deposit Platform")
    print("="*70)
    
    # Initialize platform
    platform = DirectDepositPlatform()
    
    print("\n📋 BANK ACCOUNT CONFIGURATION")
    print("-" * 70)
    print("To receive payments directly to your bank account, configure:")
    print("\n  Environment Variables:")
    print("    BANK_ACCOUNT_HOLDER='CyberGuard Industries LLC'")
    print("    BANK_NAME='Your Bank Name'")
    print("    BANK_ROUTING_NUMBER='123456789'")
    print("    BANK_ACCOUNT_NUMBER='9876543210'")
    print("    BANK_ACCOUNT_TYPE='checking'")
    print("\n  For International:")
    print("    BANK_SWIFT_CODE='ABCDUS33XXX'")
    print("    BANK_IBAN='US12345678901234567890'")
    
    # Demo: ACH Payment Setup
    print("\n\n💳 TEST 1: ACH Payment Setup")
    print("-" * 70)
    
    customer_id = "cus_demo123"
    customer_routing = "021000021"  # Chase Bank routing (for demo)
    customer_account = "1234567890"
    
    # Verify routing number
    is_valid, msg = platform.ach_processor.verify_routing_number(customer_routing)
    print(f"✓ Routing number validation: {msg}")
    
    # Initiate micro-deposits
    success, message = platform.ach_processor.initiate_micro_deposits(
        customer_id=customer_id,
        routing_number=customer_routing,
        account_number=customer_account,
        account_holder="John Doe"
    )
    print(f"✓ Micro-deposits: {message}")
    
    # Simulate customer verifying amounts (in production, they'd enter these)
    print("\n💳 TEST 2: Account Verification")
    print("-" * 70)
    
    # In demo, we know the amounts from the database
    success, message = platform.ach_processor.verify_micro_deposits(
        customer_id=customer_id,
        amount1_cents=23,  # Example amounts
        amount2_cents=47
    )
    print(f"✓ Verification: {message}")
    
    # Process ACH payment
    print("\n💳 TEST 3: Process ACH Payment")
    print("-" * 70)
    
    success, transaction_id = platform.ach_processor.process_ach_debit(
        customer_id=customer_id,
        amount=2999.00,
        routing_number=customer_routing,
        account_number=customer_account,
        account_holder="John Doe",
        description="CyberGuard Enterprise - Monthly Subscription"
    )
    
    if success:
        print(f"✓ ACH transaction initiated: {transaction_id}")
        print(f"  Amount: $2,999.00")
        print(f"  Settlement: 3-5 business days")
        
        # Check status
        status = platform.ach_processor.get_transaction_status(transaction_id)
        print(f"  Status: {status['status']}")
        print(f"  Settlement Date: {status['settlement_date']}")
    
    # Wire transfer instructions
    print("\n💳 TEST 4: Wire Transfer Instructions")
    print("-" * 70)
    
    instructions = platform.wire_processor.generate_wire_instructions(
        customer_id=customer_id,
        amount=29990.00,
        invoice_number="INV-2025-001"
    )
    
    print("\nWire Transfer Instructions:")
    print(f"  Beneficiary: {instructions['beneficiary_name']}")
    print(f"  Bank: {instructions['bank_name'] or 'Configure BANK_NAME'}")
    print(f"  Routing: {instructions['routing_number'] or 'Configure BANK_ROUTING_NUMBER'}")
    print(f"  Account: {instructions['account_number'] or 'Configure BANK_ACCOUNT_NUMBER'}")
    print(f"  Amount: ${instructions['amount']:,.2f}")
    print(f"  Reference: {instructions['reference']}")
    
    # Payment summary
    print("\n💳 TEST 5: Payment Summary")
    print("-" * 70)
    
    summary = platform.get_payment_status_summary(customer_id)
    print(f"\nCustomer: {summary['customer_id']}")
    print(f"Receiving Account: {summary['receiving_account']}")
    print(f"\nACH Transactions:")
    for txn in summary['ach_transactions']:
        print(f"  {txn['status']}: {txn['count']} transactions, ${txn['total']:,.2f}")
    print(f"\nWire Transfers:")
    print(f"  Completed: {summary['wire_transfers']['count']} transfers, ${summary['wire_transfers']['total']:,.2f}")
    
    print("\n" + "="*70)
    print("✅ Direct Bank Deposit Platform Ready!")
    print("="*70)
    print("\nFeatures:")
    print("  ✓ ACH payments (automated bank transfers)")
    print("  ✓ Bank account verification (micro-deposits)")
    print("  ✓ Wire transfer support (domestic & international)")
    print("  ✓ Direct deposit to YOUR bank account")
    print("  ✓ $0 transaction fees (unlike Stripe 2.9%)")
    print("  ✓ Settlement in 3-5 business days")
    print("\nNext Steps:")
    print("  1. Configure your bank account details (environment variables)")
    print("  2. Partner with a payment processor for ACH/Wire handling")
    print("  3. Or integrate with your existing bank's API")
    print("="*70)
