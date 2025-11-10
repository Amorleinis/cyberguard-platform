# Payment System Documentation

## CyberGuard Enterprise Platform - Payment & Billing System

### Overview

The CyberGuard payment system provides comprehensive payment processing, subscription management, and licensing capabilities for the commercial platform.

---

## Features

### 💳 Payment Processing
- **Multiple Payment Providers**
  - Stripe (Credit/Debit cards, Apple Pay, Google Pay)
  - PayPal (PayPal accounts, credit cards)
  - Direct Credit Card (PCI-compliant tokenization)
  - Bank Transfer/Wire Transfer
  - Invoice/Purchase Order

### 🔑 License Management
- **Automated License Generation**
  - Unique license key format: `CGEP-XXXX-XXXX-XXXX-XXXX`
  - Tier-based licensing (Community, Professional, Enterprise, Unlimited)
  - Expiration tracking
  - Multi-activation support (1 to unlimited)

- **License Validation**
  - Real-time validation API
  - Machine ID binding
  - Activation tracking
  - Heartbeat monitoring

### 📅 Subscription Management
- **Flexible Billing**
  - Monthly and Annual billing cycles
  - Automatic renewal
  - Trial periods (7, 14, 30 days)
  - Prorated upgrades/downgrades
  - Cancellation handling

- **Subscription Lifecycle**
  - Trial → Active → Past Due → Cancelled → Expired
  - Automatic dunning for failed payments
  - Grace periods
  - Reactivation support

### 📊 Invoicing
- **Automated Invoice Generation**
  - PDF invoices with company branding
  - Line-item details
  - Tax calculation
  - Payment terms (Net 15, Net 30, etc.)
  - Invoice history

---

## Architecture

### Components

```
payment_system.py       - Core payment logic and database
payment_gateway.py      - Payment provider integrations (Stripe, PayPal)
payment_dashboard.py    - Web UI for payment management
```

### Database Schema

**Licenses Table**
- license_key (PRIMARY KEY)
- customer_id
- tier (community, professional, enterprise, unlimited)
- status (active, expired, cancelled)
- created_at, expires_at
- max_activations, current_activations

**Subscriptions Table**
- subscription_id (PRIMARY KEY)
- customer_id (FOREIGN KEY)
- tier, status, amount, currency
- billing_cycle (monthly, annual)
- start_date, current_period_start, current_period_end
- trial_end, cancel_at_period_end

**Payments Table**
- payment_id (PRIMARY KEY)
- customer_id, subscription_id (FOREIGN KEYS)
- amount, currency, status
- provider (stripe, paypal, etc.)
- provider_transaction_id
- created_at, completed_at

**Invoices Table**
- invoice_id (PRIMARY KEY)
- customer_id, subscription_id
- amount_due, amount_paid
- status, due_date, paid_at
- invoice_pdf (file path)

---

## API Reference

### License Management

#### Generate License
```python
from scripts.payment_system import LicenseManager, LicenseTier

license_mgr = LicenseManager()
license_key = license_mgr.create_license(
    customer_id="cus_abc123",
    tier=LicenseTier.ENTERPRISE,
    duration_days=365,
    max_activations=10
)
# Returns: "CGEP-A3F2-B8E1-C9D4-F7A6"
```

#### Validate License
```python
is_valid, message = license_mgr.validate_license("CGEP-A3F2-B8E1-C9D4-F7A6")
# Returns: (True, "License is valid")
```

#### Activate License
```python
import hashlib
machine_id = hashlib.md5(b"server-001").hexdigest()
activated = license_mgr.activate_license(
    license_key="CGEP-A3F2-B8E1-C9D4-F7A6",
    machine_id=machine_id,
    ip_address="192.168.1.100"
)
```

### Payment Processing

#### Create Customer
```python
from scripts.payment_system import PaymentProcessor

payment_proc = PaymentProcessor()
customer_id = payment_proc.create_customer(
    email="john.doe@company.com",
    company_name="Acme Corporation",
    contact_name="John Doe",
    phone="+1-555-0100"
)
```

#### Create Subscription
```python
subscription_id = payment_proc.create_subscription(
    customer_id=customer_id,
    tier=LicenseTier.ENTERPRISE,
    billing_cycle="monthly",  # or "annual"
    trial_days=14
)
```

#### Process Payment
```python
success, payment_id = payment_proc.process_payment(
    customer_id=customer_id,
    amount=2999.00,
    provider=PaymentProvider.STRIPE,
    subscription_id=subscription_id,
    payment_method="card_visa_4242"
)
```

### Payment Gateway Integration

#### Stripe Checkout
```bash
POST /api/payment/checkout/stripe
Content-Type: application/json
X-API-Key: your_api_key

{
  "email": "customer@example.com",
  "price_id": "price_enterprise_monthly",
  "success_url": "https://yoursite.com/success",
  "cancel_url": "https://yoursite.com/cancel",
  "trial_days": 14
}
```

Response:
```json
{
  "id": "cs_abc123def456",
  "url": "https://checkout.stripe.com/pay/cs_abc123def456"
}
```

#### PayPal Order
```bash
POST /api/payment/checkout/paypal
Content-Type: application/json
X-API-Key: your_api_key

{
  "amount": 2999.00,
  "currency": "USD",
  "description": "CyberGuard Enterprise - Monthly"
}
```

#### Get Pricing
```bash
GET /api/pricing
```

Response:
```json
{
  "tiers": [
    {
      "name": "Community",
      "price": 0,
      "billing": "free"
    },
    {
      "name": "Professional",
      "price": 499,
      "billing": "monthly",
      "annual_price": 4990
    },
    {
      "name": "Enterprise",
      "price": 2999,
      "billing": "monthly",
      "annual_price": 29990
    }
  ]
}
```

---

## Pricing Structure

| Tier | Monthly | Annual | Savings |
|------|---------|--------|---------|
| **Community** | FREE | FREE | - |
| **Professional** | $499 | $4,990 | $998 (2 months free) |
| **Enterprise** | $2,999 | $29,990 | $5,998 (2 months free) |
| **Unlimited** | $9,999+ | Custom | Negotiable |

---

## Webhooks

### Stripe Webhooks

Configure webhook endpoint: `https://your-domain.com/api/webhooks/stripe`

**Supported Events**:
- `checkout.session.completed` - Checkout completed
- `customer.subscription.created` - New subscription
- `customer.subscription.updated` - Subscription changed
- `customer.subscription.deleted` - Subscription cancelled
- `invoice.payment_succeeded` - Payment successful
- `invoice.payment_failed` - Payment failed

### PayPal Webhooks

Configure webhook endpoint: `https://your-domain.com/api/webhooks/paypal`

**Supported Events**:
- `PAYMENT.SALE.COMPLETED` - Payment completed
- `BILLING.SUBSCRIPTION.CREATED` - Subscription created
- `BILLING.SUBSCRIPTION.CANCELLED` - Subscription cancelled

---

## Security

### PCI Compliance
- ✅ Never store raw credit card data
- ✅ Use tokenization for card processing
- ✅ TLS/SSL encryption for all transactions
- ✅ Webhook signature verification
- ✅ API key authentication

### License Security
- ✅ SHA-256 hashing for license generation
- ✅ HMAC signature verification
- ✅ Machine ID binding
- ✅ Activation limits
- ✅ Heartbeat monitoring for active licenses

---

## Testing

### Run Payment System Tests
```bash
python scripts/payment_system.py
```

Output:
```
CyberGuard Payment System - Test Suite

1. Creating customer...
   ✓ Customer created: cus_xyz789

2. Creating Enterprise subscription...
   ✓ Subscription created: sub_abc123def456

3. Processing payment...
   ✓ Payment processed: pay_123456 (Success: True)

4. Generating license key...
   ✓ License generated: CGEP-A3F2-B8E1-C9D4-F7A6

5. Validating license...
   ✓ Validation: True - License is valid

6. Activating license...
   ✓ Activation: True

✅ All tests completed successfully!
```

### Test Stripe Integration
```bash
# Set test API key
export STRIPE_API_KEY="sk_test_..."

# Run gateway tests
python scripts/payment_gateway.py
```

### Test Payment Dashboard
```bash
python scripts/payment_dashboard.py
```

Access dashboard at: http://localhost:5001

---

## Configuration

### Environment Variables

```bash
# Stripe
export STRIPE_API_KEY="sk_live_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."

# PayPal
export PAYPAL_CLIENT_ID="..."
export PAYPAL_CLIENT_SECRET="..."

# Payment API
export PAYMENT_API_KEY="your_secure_api_key"

# Email (SendGrid)
export SENDGRID_API_KEY="..."

# SMS (Twilio)
export TWILIO_ACCOUNT_SID="..."
export TWILIO_AUTH_TOKEN="..."
```

### Database Configuration

```python
# SQLite (Development)
license_mgr = LicenseManager("data/licenses.db")
payment_proc = PaymentProcessor("data/payments.db")

# PostgreSQL (Production)
license_mgr = LicenseManager("postgresql://user:pass@host/licenses")
payment_proc = PaymentProcessor("postgresql://user:pass@host/payments")
```

---

## Deployment

### 1. Install Dependencies
```bash
pip install -r requirements-payment.txt
```

### 2. Initialize Databases
```bash
python scripts/payment_system.py
```

### 3. Start Payment Gateway API
```bash
python scripts/payment_gateway.py
# API available at http://localhost:8080
```

### 4. Start Payment Dashboard
```bash
python scripts/payment_dashboard.py
# Dashboard available at http://localhost:5001
```

### 5. Configure Webhooks

**Stripe Dashboard**:
- Go to Developers → Webhooks
- Add endpoint: `https://your-domain.com/api/webhooks/stripe`
- Select events: All subscription and payment events

**PayPal Dashboard**:
- Go to Apps & Credentials → Webhooks
- Add webhook: `https://your-domain.com/api/webhooks/paypal`
- Select events: All billing and payment events

---

## Production Checklist

- [ ] Configure production Stripe/PayPal API keys
- [ ] Setup PostgreSQL database (not SQLite)
- [ ] Enable SSL/TLS certificates
- [ ] Configure email service (SendGrid)
- [ ] Setup SMS alerts (Twilio)
- [ ] Enable rate limiting
- [ ] Configure Redis caching
- [ ] Setup monitoring and logging
- [ ] Test webhook endpoints
- [ ] Configure backup strategy
- [ ] Review PCI compliance requirements
- [ ] Setup fraud detection
- [ ] Configure tax calculation
- [ ] Test payment flows end-to-end

---

## Support

### Payment Issues
- **Email**: billing@cyberguard-platform.com
- **Phone**: +1 (555) CYBER-PAY
- **Hours**: 24/7 for Enterprise+ customers

### Documentation
- API Reference: https://docs.cyberguard-platform.com/payments
- Integration Guide: https://docs.cyberguard-platform.com/integration
- Troubleshooting: https://docs.cyberguard-platform.com/troubleshooting

---

**Version**: 2.0.0  
**Last Updated**: November 10, 2025  
**Status**: Production Ready
