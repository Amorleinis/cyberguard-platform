# Bank Account Configuration Guide
# Setup instructions for direct bank deposits

## Configure Your Bank Account

To receive payments directly to your bank account, set these environment variables:

### Windows (PowerShell)
```powershell
# Basic Configuration
$env:BANK_ACCOUNT_HOLDER="CyberGuard Industries LLC"
$env:BANK_NAME="Your Bank Name (e.g., Chase, Bank of America)"
$env:BANK_ROUTING_NUMBER="123456789"  # Your 9-digit routing number
$env:BANK_ACCOUNT_NUMBER="9876543210"  # Your account number
$env:BANK_ACCOUNT_TYPE="checking"  # or "savings"

# International (Optional)
$env:BANK_SWIFT_CODE="ABCDUS33XXX"  # For international wire transfers
$env:BANK_IBAN="US12345678901234567890"  # For international transfers
```

### Linux/Mac (Bash)
```bash
# Basic Configuration
export BANK_ACCOUNT_HOLDER="CyberGuard Industries LLC"
export BANK_NAME="Your Bank Name"
export BANK_ROUTING_NUMBER="123456789"
export BANK_ACCOUNT_NUMBER="9876543210"
export BANK_ACCOUNT_TYPE="checking"

# International (Optional)
export BANK_SWIFT_CODE="ABCDUS33XXX"
export BANK_IBAN="US12345678901234567890"
```

### Permanent Configuration (.env file)
Create a file named `.env` in your project root:

```env
# CyberGuard Bank Account Configuration
BANK_ACCOUNT_HOLDER=CyberGuard Industries LLC
BANK_NAME=Chase Bank
BANK_ROUTING_NUMBER=021000021
BANK_ACCOUNT_NUMBER=1234567890
BANK_ACCOUNT_TYPE=checking

# International Transfers (Optional)
BANK_SWIFT_CODE=CHASUS33XXX
BANK_IBAN=
```

---

## Finding Your Bank Information

### Routing Number
- **Check**: Bottom left of your checks (first 9 digits)
- **Online**: Bank's website → Account Details
- **Phone**: Call your bank's customer service

### Account Number
- **Check**: Bottom of your checks (middle numbers, usually 10-12 digits)
- **Online**: Bank's website → Account Details
- **App**: Mobile banking app → Account Info

### Account Type
- **Checking**: For day-to-day transactions (recommended for business)
- **Savings**: For savings accounts (may have withdrawal limits)

### SWIFT Code (International only)
- **Find**: Bank's website → International Transfers
- **Format**: 8 or 11 characters (e.g., CHASUS33XXX)
- **Purpose**: Required for receiving international wire transfers

---

## Security Best Practices

### ⚠️ IMPORTANT - Keep Your Bank Info Secure!

1. **Never commit .env file to Git**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables in production**
   - Don't hardcode in source files
   - Use secure vault services (AWS Secrets Manager, Azure Key Vault)

3. **Limit access**
   - Only authorized personnel should have bank account details
   - Use role-based access control

4. **Monitor transactions**
   - Regularly check your bank statements
   - Enable transaction alerts
   - Review all deposits and withdrawals

---

## Payment Methods Supported

### 1. ACH (Automated Clearing House) - Recommended for US
**How it works:**
1. Customer provides their bank routing and account number
2. You send micro-deposits ($0.01-$0.99) to verify their account
3. Customer confirms the amounts
4. You can now pull payments from their account to yours
5. Funds settle in 3-5 business days

**Pros:**
- ✅ $0 transaction fees
- ✅ Automated recurring payments
- ✅ Lower cost than credit cards
- ✅ Direct bank-to-bank transfer

**Cons:**
- ❌ Slower than credit cards (3-5 days)
- ❌ Requires bank account verification
- ❌ US only

**Perfect for:**
- Monthly subscriptions
- Large payments ($1,000+)
- Enterprise customers

### 2. Wire Transfer - For Large/International Payments
**How it works:**
1. Customer requests wire instructions
2. They initiate transfer at their bank
3. Funds arrive in your account in 1-2 business days
4. You manually verify and activate their license

**Pros:**
- ✅ Works internationally
- ✅ Faster than ACH (1-2 days)
- ✅ No maximum limit
- ✅ Immediate settlement

**Cons:**
- ❌ Bank fees ($15-50 per transfer)
- ❌ Manual process
- ❌ Requires customer to visit bank

**Perfect for:**
- Annual subscriptions
- Enterprise contracts ($10,000+)
- International customers

---

## How Money Flows to Your Bank

```
Customer's Bank Account
         ↓
    [ACH Network]  (3-5 business days)
         ↓
YOUR BANK ACCOUNT 💰
```

### Example Transaction Timeline

**Day 0 (Monday):**
- Customer signs up for Enterprise plan ($2,999/month)
- You initiate ACH debit from their account

**Day 1-2 (Tuesday-Wednesday):**
- ACH network processes transaction
- Customer's bank validates funds

**Day 3 (Thursday):**
- Funds leave customer's account

**Day 4-5 (Friday-Monday):**
- Funds arrive in YOUR bank account
- **YOU GET PAID: +$2,999.00** 🎉

---

## Cost Comparison

### Stripe (Credit Cards)
- Transaction Fee: 2.9% + $0.30
- $2,999 payment = **$87.27 fee** → You receive $2,911.73
- Monthly cost for 10 customers: **$872.70 in fees**

### Direct ACH (Your Bank)
- Transaction Fee: **$0**
- $2,999 payment = **$0 fee** → You receive **$2,999.00**
- Monthly cost for 10 customers: **$0 in fees**

### **Annual Savings on 10 Enterprise Customers:**
- Stripe fees: $10,472.40/year
- ACH fees: **$0/year**
- **YOU SAVE: $10,472.40** 💰

---

## Setup Checklist

### ✅ Step 1: Get Bank Account Details
- [ ] Routing number (9 digits)
- [ ] Account number (10-12 digits)
- [ ] Account type (checking/savings)
- [ ] Bank name
- [ ] Account holder name (business or personal)

### ✅ Step 2: Configure Platform
- [ ] Set environment variables (see commands above)
- [ ] Test configuration with demo mode
- [ ] Verify bank info displays correctly

### ✅ Step 3: Choose Payment Processor
You need a partner to actually move money via ACH. Options:

**Option A: Use Your Bank's API** (If available)
- Many banks offer ACH APIs
- Contact your bank's business services
- Usually cheapest option

**Option B: Payment Platform**
- Dwolla (ACH specialist) - $0.25/transaction
- Plaid (bank verification) - $0.25/verification
- Stripe ACH - 0.8% capped at $5

**Option C: Start with Stripe, Migrate Later**
- Use Stripe initially (easy setup)
- Switch to direct ACH once you have volume
- Keep this code ready for when you scale

### ✅ Step 4: Test Payment Flow
```bash
# Run the platform
python scripts/direct_bank_platform.py

# Test output will show:
# - Your configured bank account (masked)
# - ACH payment processing
# - Wire transfer instructions
```

### ✅ Step 5: Go Live
- [ ] Verify bank account can receive ACH
- [ ] Enable wire transfer acceptance at your bank
- [ ] Setup transaction monitoring
- [ ] Configure automated reconciliation

---

## FAQ

**Q: Is it safe to store my bank account number in environment variables?**
A: Yes, IF you follow security best practices:
- Don't commit to Git
- Use encryption at rest
- Limit server access
- Monitor for unauthorized access

**Q: Can I use my personal bank account?**
A: Yes, but recommended to open a business account for:
- Better accounting separation
- Higher transaction limits
- Professional appearance
- Tax benefits

**Q: How do I handle refunds?**
A: ACH credits (reverse transactions):
1. Initiate ACH credit to customer's account
2. Funds leave your account
3. Arrive in customer's account in 3-5 days

**Q: What about credit card payments?**
A: You can offer BOTH:
- Credit cards via Stripe (instant, 2.9% fee)
- ACH direct (3-5 days, $0 fee)
- Let customers choose based on their preference

**Q: Do I need special licenses or permits?**
A: For ACH processing, you need:
- Business bank account
- EIN (Employer Identification Number) or SSN
- Partnership with ACH processor (or use bank's API)
- Compliance with NACHA rules (your processor handles this)

---

## Next Steps

1. **Get Your Bank Info Ready**
   - Call your bank if needed
   - Have routing and account numbers handy

2. **Configure the Platform**
   ```powershell
   # Copy this and fill in YOUR details
   $env:BANK_ACCOUNT_HOLDER="Your Name or Business Name"
   $env:BANK_NAME="Your Bank"
   $env:BANK_ROUTING_NUMBER="your 9-digit routing"
   $env:BANK_ACCOUNT_NUMBER="your account number"
   ```

3. **Test It**
   ```bash
   python scripts/direct_bank_platform.py
   ```

4. **Choose Payment Partner**
   - Contact your bank about ACH capabilities
   - OR sign up for Dwolla/Plaid
   - OR start with Stripe ACH

5. **Start Accepting Payments**
   - Customers pay you directly
   - Money goes straight to YOUR bank
   - No middleman taking 3%

---

**Ready to save thousands in payment fees?** 🚀

Configure your bank account and start receiving payments directly!
