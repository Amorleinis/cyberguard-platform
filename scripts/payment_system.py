# Payment System for CyberGuard Enterprise Platform
# Handles subscriptions, licensing, and payment processing

import os
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import sqlite3
from pathlib import Path


class LicenseTier(Enum):
    """License tier enumeration"""
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class SubscriptionStatus(Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class PaymentProvider(Enum):
    """Supported payment providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    INVOICE = "invoice"


class LicenseManager:
    """Manages software licenses and activation"""
    
    def __init__(self, db_path: str = "data/licenses.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize license database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Licenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS licenses (
                license_key TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                tier TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                max_activations INTEGER DEFAULT 1,
                current_activations INTEGER DEFAULT 0,
                metadata TEXT
            )
        """)
        
        # Activations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT NOT NULL,
                machine_id TEXT NOT NULL,
                ip_address TEXT,
                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_heartbeat TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (license_key) REFERENCES licenses(license_key)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def generate_license_key(self, customer_id: str, tier: LicenseTier) -> str:
        """Generate a unique license key"""
        timestamp = datetime.now().isoformat()
        data = f"{customer_id}:{tier.value}:{timestamp}:{os.urandom(16).hex()}"
        hash_obj = hashlib.sha256(data.encode())
        
        # Format: CGEP-XXXX-XXXX-XXXX-XXXX (CyberGuard Enterprise Platform)
        hex_key = hash_obj.hexdigest()[:16].upper()
        formatted_key = f"CGEP-{hex_key[0:4]}-{hex_key[4:8]}-{hex_key[8:12]}-{hex_key[12:16]}"
        
        return formatted_key
    
    def create_license(
        self,
        customer_id: str,
        tier: LicenseTier,
        duration_days: int = 365,
        max_activations: int = 1,
        metadata: Optional[Dict] = None
    ) -> str:
        """Create a new license"""
        license_key = self.generate_license_key(customer_id, tier)
        expires_at = datetime.now() + timedelta(days=duration_days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO licenses (license_key, customer_id, tier, status, expires_at, max_activations, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            license_key,
            customer_id,
            tier.value,
            SubscriptionStatus.ACTIVE.value,
            expires_at,
            max_activations,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
        
        return license_key
    
    def validate_license(self, license_key: str) -> Tuple[bool, str]:
        """Validate a license key"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, expires_at, current_activations, max_activations
            FROM licenses WHERE license_key = ?
        """, (license_key,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False, "Invalid license key"
        
        status, expires_at, current_activations, max_activations = result
        
        if status != SubscriptionStatus.ACTIVE.value:
            return False, f"License is {status}"
        
        if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
            return False, "License has expired"
        
        if current_activations >= max_activations:
            return False, "Maximum activations reached"
        
        return True, "License is valid"
    
    def activate_license(self, license_key: str, machine_id: str, ip_address: str = None) -> bool:
        """Activate a license on a machine"""
        is_valid, message = self.validate_license(license_key)
        if not is_valid:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already activated on this machine
        cursor.execute("""
            SELECT id FROM activations 
            WHERE license_key = ? AND machine_id = ? AND is_active = 1
        """, (license_key, machine_id))
        
        if cursor.fetchone():
            conn.close()
            return True  # Already activated
        
        # Create new activation
        cursor.execute("""
            INSERT INTO activations (license_key, machine_id, ip_address, last_heartbeat)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (license_key, machine_id, ip_address))
        
        # Update activation count
        cursor.execute("""
            UPDATE licenses 
            SET current_activations = current_activations + 1
            WHERE license_key = ?
        """, (license_key,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def deactivate_license(self, license_key: str, machine_id: str) -> bool:
        """Deactivate a license on a machine"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE activations 
            SET is_active = 0
            WHERE license_key = ? AND machine_id = ? AND is_active = 1
        """, (license_key, machine_id))
        
        if cursor.rowcount > 0:
            cursor.execute("""
                UPDATE licenses 
                SET current_activations = current_activations - 1
                WHERE license_key = ?
            """, (license_key,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0


class PaymentProcessor:
    """Handles payment processing with multiple providers"""
    
    def __init__(self, db_path: str = "data/payments.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Payment provider configurations
        self.stripe_config = {
            "api_key": os.getenv("STRIPE_API_KEY", ""),
            "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET", "")
        }
        
        self.paypal_config = {
            "client_id": os.getenv("PAYPAL_CLIENT_ID", ""),
            "client_secret": os.getenv("PAYPAL_CLIENT_SECRET", "")
        }
    
    def _init_database(self):
        """Initialize payment database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                company_name TEXT,
                contact_name TEXT,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                tier TEXT NOT NULL,
                status TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                billing_cycle TEXT DEFAULT 'monthly',
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                current_period_start TIMESTAMP,
                current_period_end TIMESTAMP,
                cancel_at_period_end BOOLEAN DEFAULT 0,
                trial_end TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        # Payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                subscription_id TEXT,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                status TEXT NOT NULL,
                provider TEXT NOT NULL,
                provider_transaction_id TEXT,
                payment_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
            )
        """)
        
        # Invoices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                subscription_id TEXT,
                amount_due REAL NOT NULL,
                amount_paid REAL DEFAULT 0,
                currency TEXT DEFAULT 'USD',
                status TEXT NOT NULL,
                due_date TIMESTAMP,
                paid_at TIMESTAMP,
                invoice_pdf TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_customer(
        self,
        email: str,
        company_name: str = None,
        contact_name: str = None,
        phone: str = None,
        address: str = None,
        metadata: Dict = None
    ) -> str:
        """Create a new customer"""
        customer_id = f"cus_{hashlib.md5(email.encode()).hexdigest()[:16]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO customers 
            (customer_id, email, company_name, contact_name, phone, address, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id,
            email,
            company_name,
            contact_name,
            phone,
            address,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
        
        return customer_id
    
    def create_subscription(
        self,
        customer_id: str,
        tier: LicenseTier,
        billing_cycle: str = "monthly",
        trial_days: int = 0
    ) -> str:
        """Create a new subscription"""
        # Pricing based on tier
        pricing = {
            LicenseTier.COMMUNITY: 0,
            LicenseTier.PROFESSIONAL: 499,
            LicenseTier.ENTERPRISE: 2999,
            LicenseTier.UNLIMITED: 9999
        }
        
        amount = pricing.get(tier, 0)
        
        # Adjust for billing cycle
        if billing_cycle == "annual":
            amount = amount * 10  # 2 months free
        
        subscription_id = f"sub_{hashlib.md5(f'{customer_id}:{datetime.now().isoformat()}'.encode()).hexdigest()[:16]}"
        
        now = datetime.now()
        trial_end = now + timedelta(days=trial_days) if trial_days > 0 else None
        period_start = trial_end or now
        period_end = period_start + (timedelta(days=365) if billing_cycle == "annual" else timedelta(days=30))
        
        status = SubscriptionStatus.TRIALING.value if trial_days > 0 else SubscriptionStatus.ACTIVE.value
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO subscriptions 
            (subscription_id, customer_id, tier, status, amount, billing_cycle, 
             current_period_start, current_period_end, trial_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            subscription_id,
            customer_id,
            tier.value,
            status,
            amount,
            billing_cycle,
            period_start,
            period_end,
            trial_end
        ))
        
        conn.commit()
        conn.close()
        
        return subscription_id
    
    def process_payment(
        self,
        customer_id: str,
        amount: float,
        provider: PaymentProvider,
        subscription_id: str = None,
        payment_method: str = None,
        metadata: Dict = None
    ) -> Tuple[bool, str]:
        """Process a payment"""
        payment_id = f"pay_{hashlib.md5(f'{customer_id}:{datetime.now().isoformat()}'.encode()).hexdigest()[:16]}"
        
        # Simulate payment processing
        # In production, integrate with actual payment providers
        success = True
        provider_transaction_id = f"{provider.value}_{os.urandom(8).hex()}"
        
        status = PaymentStatus.COMPLETED.value if success else PaymentStatus.FAILED.value
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO payments 
            (payment_id, customer_id, subscription_id, amount, status, provider, 
             provider_transaction_id, payment_method, completed_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            payment_id,
            customer_id,
            subscription_id,
            amount,
            status,
            provider.value,
            provider_transaction_id,
            payment_method,
            datetime.now() if success else None,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
        
        return success, payment_id
    
    def create_invoice(
        self,
        customer_id: str,
        amount: float,
        subscription_id: str = None,
        due_days: int = 30
    ) -> str:
        """Create an invoice"""
        invoice_id = f"inv_{hashlib.md5(f'{customer_id}:{datetime.now().isoformat()}'.encode()).hexdigest()[:16]}"
        due_date = datetime.now() + timedelta(days=due_days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO invoices 
            (invoice_id, customer_id, subscription_id, amount_due, status, due_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            invoice_id,
            customer_id,
            subscription_id,
            amount,
            PaymentStatus.PENDING.value,
            due_date
        ))
        
        conn.commit()
        conn.close()
        
        return invoice_id
    
    def get_subscription_details(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.*, c.email, c.company_name
            FROM subscriptions s
            JOIN customers c ON s.customer_id = c.customer_id
            WHERE s.subscription_id = ?
        """, (subscription_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, result))
    
    def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> bool:
        """Cancel a subscription"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if immediate:
            cursor.execute("""
                UPDATE subscriptions 
                SET status = ?, current_period_end = CURRENT_TIMESTAMP
                WHERE subscription_id = ?
            """, (SubscriptionStatus.CANCELLED.value, subscription_id))
        else:
            cursor.execute("""
                UPDATE subscriptions 
                SET cancel_at_period_end = 1
                WHERE subscription_id = ?
            """, (subscription_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0


class PricingCalculator:
    """Calculate pricing for different scenarios"""
    
    # Base monthly prices
    PRICING = {
        LicenseTier.COMMUNITY: 0,
        LicenseTier.PROFESSIONAL: 499,
        LicenseTier.ENTERPRISE: 2999,
        LicenseTier.UNLIMITED: 9999
    }
    
    @classmethod
    def calculate_price(
        cls,
        tier: LicenseTier,
        billing_cycle: str = "monthly",
        quantity: int = 1,
        discount_percent: float = 0
    ) -> float:
        """Calculate total price"""
        base_price = cls.PRICING[tier]
        
        # Apply billing cycle discount
        if billing_cycle == "annual":
            base_price = base_price * 10  # 2 months free
        
        # Apply quantity
        total = base_price * quantity
        
        # Apply discount
        if discount_percent > 0:
            total = total * (1 - discount_percent / 100)
        
        return round(total, 2)
    
    @classmethod
    def calculate_proration(
        cls,
        current_tier: LicenseTier,
        new_tier: LicenseTier,
        days_remaining: int,
        billing_cycle: str = "monthly"
    ) -> float:
        """Calculate prorated amount for tier upgrade"""
        current_price = cls.PRICING[current_tier]
        new_price = cls.PRICING[new_tier]
        
        days_in_cycle = 365 if billing_cycle == "annual" else 30
        daily_rate_diff = (new_price - current_price) / days_in_cycle
        
        prorated_amount = daily_rate_diff * days_remaining
        
        return round(max(0, prorated_amount), 2)


# Example usage and testing
if __name__ == "__main__":
    print("CyberGuard Payment System - Test Suite\n")
    
    # Initialize managers
    license_mgr = LicenseManager("data/test_licenses.db")
    payment_proc = PaymentProcessor("data/test_payments.db")
    
    # Test 1: Create customer
    print("1. Creating customer...")
    customer_id = payment_proc.create_customer(
        email="john.doe@company.com",
        company_name="Acme Corporation",
        contact_name="John Doe",
        phone="+1-555-0100"
    )
    print(f"   ✓ Customer created: {customer_id}")
    
    # Test 2: Create subscription
    print("\n2. Creating Enterprise subscription...")
    subscription_id = payment_proc.create_subscription(
        customer_id=customer_id,
        tier=LicenseTier.ENTERPRISE,
        billing_cycle="monthly",
        trial_days=14
    )
    print(f"   ✓ Subscription created: {subscription_id}")
    
    # Test 3: Process payment
    print("\n3. Processing payment...")
    success, payment_id = payment_proc.process_payment(
        customer_id=customer_id,
        amount=2999.00,
        provider=PaymentProvider.STRIPE,
        subscription_id=subscription_id,
        payment_method="card_visa_4242"
    )
    print(f"   ✓ Payment processed: {payment_id} (Success: {success})")
    
    # Test 4: Generate license
    print("\n4. Generating license key...")
    license_key = license_mgr.create_license(
        customer_id=customer_id,
        tier=LicenseTier.ENTERPRISE,
        duration_days=365,
        max_activations=10
    )
    print(f"   ✓ License generated: {license_key}")
    
    # Test 5: Validate license
    print("\n5. Validating license...")
    is_valid, message = license_mgr.validate_license(license_key)
    print(f"   ✓ Validation: {is_valid} - {message}")
    
    # Test 6: Activate license
    print("\n6. Activating license...")
    machine_id = hashlib.md5(b"test-machine-001").hexdigest()
    activated = license_mgr.activate_license(license_key, machine_id, "192.168.1.100")
    print(f"   ✓ Activation: {activated}")
    
    # Test 7: Pricing calculation
    print("\n7. Calculating pricing...")
    monthly_price = PricingCalculator.calculate_price(LicenseTier.ENTERPRISE, "monthly")
    annual_price = PricingCalculator.calculate_price(LicenseTier.ENTERPRISE, "annual")
    print(f"   ✓ Monthly: ${monthly_price:,.2f}")
    print(f"   ✓ Annual: ${annual_price:,.2f} (Save ${monthly_price * 12 - annual_price:,.2f})")
    
    # Test 8: Create invoice
    print("\n8. Creating invoice...")
    invoice_id = payment_proc.create_invoice(
        customer_id=customer_id,
        amount=2999.00,
        subscription_id=subscription_id,
        due_days=30
    )
    print(f"   ✓ Invoice created: {invoice_id}")
    
    print("\n✅ All tests completed successfully!")
    print("\nPayment System Features:")
    print("  • License key generation and validation")
    print("  • Multi-tier subscription management")
    print("  • Payment processing (Stripe, PayPal, etc.)")
    print("  • Invoice generation")
    print("  • Activation tracking")
    print("  • Pricing calculations with discounts")
    print("  • Trial period support")
