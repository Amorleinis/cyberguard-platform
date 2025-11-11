#!/usr/bin/env python3
"""
CyberGuard Industries - Bank Account Configuration Wizard

Interactive setup wizard to configure your business bank account
for direct deposits (ACH and Wire transfers).

This wizard will:
1. Collect your bank account information
2. Validate routing numbers
3. Generate secure environment variable configuration
4. Test the setup
5. Provide next steps

Usage:
    python configure_bank_account.py

SECURITY NOTES:
- Never commit .env file to Git
- Store credentials securely
- Use environment variables in production
- Keep backup of credentials in secure location
"""

import os
import sys
import hashlib
import getpass
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}→ {text}{Colors.ENDC}")

def validate_routing_number(routing):
    """Validate routing number using ABA checksum algorithm"""
    if not routing or len(routing) != 9:
        return False
    
    try:
        digits = [int(d) for d in routing]
        checksum = (
            3 * (digits[0] + digits[3] + digits[6]) +
            7 * (digits[1] + digits[4] + digits[7]) +
            (digits[2] + digits[5] + digits[8])
        )
        return checksum % 10 == 0
    except (ValueError, IndexError):
        return False

def mask_account_number(account_number):
    """Mask account number for display"""
    if len(account_number) <= 4:
        return "*" * len(account_number)
    return "*" * (len(account_number) - 4) + account_number[-4:]

def get_input(prompt, required=True, sensitive=False):
    """Get user input with validation"""
    while True:
        if sensitive:
            value = getpass.getpass(f"{Colors.OKCYAN}{prompt}: {Colors.ENDC}")
        else:
            value = input(f"{Colors.OKCYAN}{prompt}: {Colors.ENDC}").strip()
        
        if value or not required:
            return value
        print_error("This field is required. Please try again.")

def confirm(prompt):
    """Get yes/no confirmation"""
    while True:
        response = input(f"{Colors.WARNING}{prompt} (yes/no): {Colors.ENDC}").strip().lower()
        if response in ['yes', 'y']:
            return True
        if response in ['no', 'n']:
            return False
        print_error("Please answer 'yes' or 'no'")

def main():
    """Main configuration wizard"""
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🏦  CYBERGUARD BANK ACCOUNT CONFIGURATION WIZARD".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{Colors.ENDC}\n")
    
    print_info("This wizard will help you configure your business bank account")
    print_info("for receiving direct payments via ACH and Wire transfers.")
    print()
    
    # Security warning
    print_warning("SECURITY REMINDER:")
    print("  • Your bank details will be stored in environment variables")
    print("  • Never commit the .env file to Git")
    print("  • Keep backup of credentials in secure location (password manager)")
    print("  • Use production-grade secrets management in production\n")
    
    if not confirm("Do you want to continue?"):
        print("\nConfiguration cancelled.")
        return
    
    # Collect bank information
    print_header("STEP 1: BUSINESS INFORMATION")
    
    account_holder = get_input("Legal business name (as appears on bank account)")
    email = get_input("Business email address")
    phone = get_input("Business phone number", required=False)
    
    # Bank details
    print_header("STEP 2: BANK ACCOUNT DETAILS")
    
    print_info("You can find this information on:")
    print("  • Your bank's online portal")
    print("  • Bottom of your business checks")
    print("  • Bank statement")
    print("  • Contact your bank directly\n")
    
    bank_name = get_input("Bank name (e.g., Chase, Bank of America)")
    
    # Routing number with validation
    while True:
        routing_number = get_input("Routing number (9 digits)")
        
        if len(routing_number) != 9 or not routing_number.isdigit():
            print_error("Routing number must be exactly 9 digits")
            continue
        
        if validate_routing_number(routing_number):
            print_success(f"Routing number validated: {routing_number}")
            break
        else:
            print_error("Invalid routing number (failed ABA checksum)")
            if confirm("Continue anyway? (not recommended)"):
                print_warning("Using unvalidated routing number")
                break
    
    # Account number (sensitive)
    account_number = get_input("Account number", sensitive=True)
    account_number_confirm = get_input("Confirm account number", sensitive=True)
    
    if account_number != account_number_confirm:
        print_error("Account numbers don't match. Exiting for security.")
        return
    
    print_success(f"Account number confirmed: {mask_account_number(account_number)}")
    
    # Account type
    print_info("\nAccount type:")
    print("  1. Checking (recommended for business)")
    print("  2. Savings")
    account_type_choice = get_input("Select account type (1 or 2)")
    account_type = "checking" if account_type_choice == "1" else "savings"
    
    # International (optional)
    print_header("STEP 3: INTERNATIONAL PAYMENTS (Optional)")
    
    if confirm("Will you accept international wire transfers?"):
        swift_code = get_input("SWIFT/BIC code (8 or 11 characters)", required=False)
        iban = get_input("IBAN (if applicable)", required=False)
    else:
        swift_code = ""
        iban = ""
    
    # Review information
    print_header("STEP 4: REVIEW YOUR INFORMATION")
    
    print(f"\n{Colors.BOLD}Business Information:{Colors.ENDC}")
    print(f"  Account Holder:  {account_holder}")
    print(f"  Email:           {email}")
    print(f"  Phone:           {phone or 'Not provided'}")
    
    print(f"\n{Colors.BOLD}Bank Details:{Colors.ENDC}")
    print(f"  Bank Name:       {bank_name}")
    print(f"  Routing Number:  {routing_number}")
    print(f"  Account Number:  {mask_account_number(account_number)}")
    print(f"  Account Type:    {account_type.title()}")
    
    if swift_code or iban:
        print(f"\n{Colors.BOLD}International:{Colors.ENDC}")
        if swift_code:
            print(f"  SWIFT Code:      {swift_code}")
        if iban:
            print(f"  IBAN:            {iban}")
    
    print()
    
    if not confirm("Is this information correct?"):
        print("\nConfiguration cancelled. Please run the wizard again.")
        return
    
    # Generate .env file
    print_header("STEP 5: GENERATING CONFIGURATION")
    
    env_content = f"""# CyberGuard Industries - Bank Account Configuration
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 
# SECURITY WARNING:
# - Never commit this file to Git
# - Keep backup in secure location (password manager)
# - Use secrets management in production (AWS Secrets Manager, etc.)

# Business Information
BANK_ACCOUNT_HOLDER="{account_holder}"
BUSINESS_EMAIL="{email}"
BUSINESS_PHONE="{phone}"

# Bank Account Details
BANK_NAME="{bank_name}"
BANK_ROUTING_NUMBER="{routing_number}"
BANK_ACCOUNT_NUMBER="{account_number}"
BANK_ACCOUNT_TYPE="{account_type}"

# International (if applicable)
BANK_SWIFT_CODE="{swift_code}"
BANK_IBAN="{iban}"

# Payment Platform Configuration
PAYMENT_PLATFORM="direct_bank"
ACH_ENABLED="true"
WIRE_ENABLED="true"

# Notification Settings
PAYMENT_NOTIFICATION_EMAIL="{email}"

# Security
ACCOUNT_NUMBER_HASH="{hashlib.sha256(account_number.encode()).hexdigest()}"
"""
    
    # Save .env file
    env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        print_success(f"Configuration saved to: {env_file_path}")
    except Exception as e:
        print_error(f"Failed to save configuration: {e}")
        print("\nPlease save the following content manually to .env file:")
        print(f"\n{Colors.OKCYAN}{env_content}{Colors.ENDC}")
        return
    
    # Create .gitignore entry
    gitignore_path = os.path.join(os.path.dirname(__file__), '..', '.gitignore')
    
    try:
        gitignore_content = ""
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
        
        if '.env' not in gitignore_content:
            with open(gitignore_path, 'a') as f:
                f.write("\n# Environment variables (bank account credentials)\n")
                f.write(".env\n")
                f.write(".env.*\n")
            print_success("Added .env to .gitignore")
    except Exception as e:
        print_warning(f"Could not update .gitignore: {e}")
    
    # Test configuration
    print_header("STEP 6: TESTING CONFIGURATION")
    
    try:
        from direct_bank_platform import DirectDepositPlatform, BankAccount
        
        # Load environment variables
        for line in env_content.split('\n'):
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"')
        
        platform = DirectDepositPlatform()
        print_success("Direct Bank Platform initialized successfully")
        
        # Validate routing number again
        if platform.ach_processor.validate_routing_number(routing_number):
            print_success("Routing number validation passed")
        else:
            print_warning("Routing number validation failed (may still work)")
        
        print_success("Configuration test completed")
        
    except Exception as e:
        print_error(f"Configuration test failed: {e}")
        print_warning("You may need to install dependencies: pip install -r requirements-payment.txt")
    
    # Next steps
    print_header("✅ CONFIGURATION COMPLETE!")
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}Your bank account is now configured!{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}\n")
    
    print("1. BACKUP YOUR CREDENTIALS:")
    print(f"   → Save to password manager (1Password, LastPass, etc.)")
    print(f"   → Store .env file in secure location")
    print(f"   → File location: {env_file_path}\n")
    
    print("2. VERIFY .ENV IS NOT IN GIT:")
    print("   → Check .gitignore includes .env")
    print("   → Run: git status")
    print("   → Ensure .env is not listed\n")
    
    print("3. CHOOSE ACH/WIRE PROCESSOR:")
    print("   → Dwolla (dwolla.com) - $0.25/transaction")
    print("   → Plaid (plaid.com) - $0.25/verification")
    print("   → Stripe ACH - 0.8% capped at $5")
    print("   → Your bank's API (contact bank)\n")
    
    print("4. TEST WITH SMALL PAYMENT:")
    print("   → Start with $1 test transaction")
    print("   → Verify funds arrive correctly")
    print("   → Check settlement time (3-5 days)\n")
    
    print("5. START ACCEPTING PAYMENTS:")
    print("   → Update payment gateway with ACH details")
    print("   → Enable ACH on pricing page")
    print("   → Promote $0 fee advantage\n")
    
    print(f"{Colors.BOLD}Cost Savings Reminder:{Colors.ENDC}")
    print(f"  Stripe:     $2,999 payment - $87 fee = $2,912 (97.1%)")
    print(f"  Direct ACH: $2,999 payment - $0 fee = $2,999 (100%)")
    print(f"  {Colors.OKGREEN}Annual Savings: $10,440+ on 10 Enterprise customers!{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Security Reminders:{Colors.ENDC}")
    print("  ✓ .env file is in .gitignore")
    print("  ✓ Never share account credentials")
    print("  ✓ Monitor account for unauthorized transactions")
    print("  ✓ Enable 2FA on bank account")
    print("  ✓ Review transactions weekly\n")
    
    print(f"{Colors.OKCYAN}For help, see: docs/BANK_SETUP_GUIDE.md{Colors.ENDC}\n")
    
    # Save summary
    summary_file = os.path.join(os.path.dirname(__file__), 'bank_config_summary.txt')
    summary_content = f"""CyberGuard Industries - Bank Account Configuration Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Account Holder: {account_holder}
Bank Name: {bank_name}
Routing Number: {routing_number}
Account Number: {mask_account_number(account_number)}
Account Type: {account_type.title()}

Configuration File: {env_file_path}
Status: Successfully configured

Next Steps:
1. Backup credentials to password manager
2. Verify .env is not in Git
3. Choose ACH processor (Dwolla, Plaid, Stripe)
4. Test with small payment
5. Start accepting payments

For questions: See docs/BANK_SETUP_GUIDE.md
"""
    
    try:
        with open(summary_file, 'w') as f:
            f.write(summary_content)
        print_success(f"Summary saved to: {summary_file}")
    except:
        pass
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 Setup complete! You're ready to receive payments directly to your bank!{Colors.ENDC}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Configuration cancelled by user.{Colors.ENDC}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.FAIL}Error: {e}{Colors.ENDC}\n")
        sys.exit(1)
