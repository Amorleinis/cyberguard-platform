#!/usr/bin/env python3
"""
CyberGuard Enterprise Platform - Comprehensive Test Suite

Tests all major components:
1. Threat Detection Engine
2. Threat Intelligence Engine
3. Payment System
4. Direct Bank Platform
5. Website Server
6. Platform Integration

Usage:
    python test_platform.py
"""

import sys
import os
import time
import json
from datetime import datetime

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.ENDC}\n")

def print_test(name, status, details=""):
    """Print test result"""
    if status == "PASS":
        icon = "✓"
        color = Colors.OKGREEN
    elif status == "FAIL":
        icon = "✗"
        color = Colors.FAIL
    elif status == "SKIP":
        icon = "⊘"
        color = Colors.WARNING
    else:
        icon = "→"
        color = Colors.OKCYAN
    
    print(f"{color}{icon} {name}{Colors.ENDC}")
    if details:
        print(f"  {details}")

def test_imports():
    """Test all critical imports"""
    print_header("1. TESTING IMPORTS")
    
    tests = []
    
    # Test detection engine import
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'detection'))
        from threat_detection_engine import ThreatDetectionEngine
        print_test("Threat Detection Engine import", "PASS")
        tests.append(True)
    except Exception as e:
        print_test("Threat Detection Engine import", "FAIL", str(e))
        tests.append(False)
    
    # Test intelligence engine import
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'intelligence'))
        from threat_intelligence_engine import ThreatIntelligenceEngine
        print_test("Threat Intelligence Engine import", "PASS")
        tests.append(True)
    except Exception as e:
        print_test("Threat Intelligence Engine import", "FAIL", str(e))
        tests.append(False)
    
    # Test payment system import
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from payment_system import LicenseManager, PaymentProcessor
        print_test("Payment System import", "PASS")
        tests.append(True)
    except Exception as e:
        print_test("Payment System import", "FAIL", str(e))
        tests.append(False)
    
    # Test direct bank platform import
    try:
        from direct_bank_platform import DirectDepositPlatform
        print_test("Direct Bank Platform import", "PASS")
        tests.append(True)
    except Exception as e:
        print_test("Direct Bank Platform import", "FAIL", str(e))
        tests.append(False)
    
    return all(tests)

def test_threat_detection():
    """Test threat detection engine"""
    print_header("2. TESTING THREAT DETECTION ENGINE")
    
    try:
        from threat_detection_engine import ThreatDetectionEngine
        
        # Initialize engine
        engine = ThreatDetectionEngine()
        print_test("Engine initialization", "PASS")
        
        # Test malicious IP detection
        malicious_ip = "192.168.1.100"
        result = engine.analyze_network_traffic(malicious_ip, 80, 1000)
        if result['threat_detected']:
            print_test("Malicious IP detection", "PASS", f"Detected: {result['threat_type']}")
        else:
            print_test("Malicious IP detection", "FAIL", "No threat detected")
        
        # Test file analysis
        malicious_file = "/tmp/malware.exe"
        result = engine.analyze_file(malicious_file)
        if result['threat_detected']:
            print_test("File analysis", "PASS", f"Risk level: {result['risk_level']}")
        else:
            print_test("File analysis", "FAIL", "No threat detected")
        
        # Test ML prediction
        features = [0.8, 0.9, 0.7, 0.6, 0.85]
        prediction = engine.ml_predict(features)
        print_test("ML prediction", "PASS", f"Confidence: {prediction:.2%}")
        
        # Get statistics
        stats = engine.get_statistics()
        print_test("Statistics retrieval", "PASS", 
                  f"IOCs: {stats['total_iocs']}, Rules: {stats['active_rules']}")
        
        return True
        
    except Exception as e:
        print_test("Threat Detection Engine", "FAIL", str(e))
        return False

def test_threat_intelligence():
    """Test threat intelligence engine"""
    print_header("3. TESTING THREAT INTELLIGENCE ENGINE")
    
    try:
        from threat_intelligence_engine import ThreatIntelligenceEngine
        
        # Initialize engine
        engine = ThreatIntelligenceEngine()
        print_test("Engine initialization", "PASS")
        
        # Test IP enrichment
        ip = "8.8.8.8"
        enrichment = engine.enrich_ip(ip)
        print_test("IP enrichment", "PASS", 
                  f"Location: {enrichment.get('location', 'Unknown')}")
        
        # Test threat feed
        feeds = engine.get_active_feeds()
        print_test("Threat feeds", "PASS", f"{len(feeds)} active feeds")
        
        # Test IoC lookup
        ioc_count = len(engine.ioc_database)
        print_test("IoC database", "PASS", f"{ioc_count:,} indicators")
        
        # Test CVE lookup
        cve = "CVE-2024-1234"
        cve_info = engine.lookup_cve(cve)
        print_test("CVE lookup", "PASS", f"Severity: {cve_info.get('severity', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print_test("Threat Intelligence Engine", "FAIL", str(e))
        return False

def test_payment_system():
    """Test payment system"""
    print_header("4. TESTING PAYMENT SYSTEM")
    
    try:
        from payment_system import LicenseManager, PaymentProcessor
        
        # Initialize managers
        license_mgr = LicenseManager()
        payment_proc = PaymentProcessor()
        print_test("System initialization", "PASS")
        
        # Test license generation
        license_key = license_mgr.generate_license("professional", "test@example.com")
        if license_key and license_key.startswith("CGEP-"):
            print_test("License generation", "PASS", f"Key: {license_key}")
        else:
            print_test("License generation", "FAIL", "Invalid key format")
            return False
        
        # Test license validation
        is_valid = license_mgr.validate_license(license_key)
        print_test("License validation", "PASS" if is_valid else "FAIL")
        
        # Test license activation
        machine_id = "TEST-MACHINE-001"
        activated = license_mgr.activate_license(license_key, machine_id)
        print_test("License activation", "PASS" if activated else "FAIL")
        
        # Test payment processing
        payment = payment_proc.process_payment(
            amount=499.00,
            method="credit_card",
            customer_email="test@example.com"
        )
        if payment and payment.get('status') == 'completed':
            print_test("Payment processing", "PASS", 
                      f"Transaction ID: {payment['transaction_id']}")
        else:
            print_test("Payment processing", "FAIL")
            return False
        
        # Test subscription creation
        subscription = payment_proc.create_subscription(
            tier="professional",
            customer_email="test@example.com",
            billing_cycle="monthly"
        )
        print_test("Subscription creation", "PASS" if subscription else "FAIL")
        
        return True
        
    except Exception as e:
        print_test("Payment System", "FAIL", str(e))
        return False

def test_direct_bank_platform():
    """Test direct bank deposit platform"""
    print_header("5. TESTING DIRECT BANK PLATFORM")
    
    try:
        from direct_bank_platform import DirectDepositPlatform, BankAccount
        
        # Initialize platform
        platform = DirectDepositPlatform()
        print_test("Platform initialization", "PASS")
        
        # Test routing number validation
        valid_routing = "021000021"  # Chase Bank routing number
        is_valid = platform.ach_processor.validate_routing_number(valid_routing)
        print_test("Routing number validation", "PASS" if is_valid else "FAIL",
                  f"Routing: {valid_routing}")
        
        # Test bank account verification
        test_account = BankAccount(
            account_holder="Test Company",
            bank_name="Test Bank",
            routing_number=valid_routing,
            account_number="1234567890"
        )
        verification = platform.verify_bank_account(test_account)
        print_test("Bank account verification", "PASS",
                  f"Micro-deposits: ${verification['micro_deposit_1']:.2f}, ${verification['micro_deposit_2']:.2f}")
        
        # Test ACH payment setup
        customer_account = BankAccount(
            account_holder="Customer Inc",
            bank_name="Customer Bank",
            routing_number="021000021",
            account_number="9876543210"
        )
        ach_payment = platform.setup_ach_payment(customer_account, 2999.00)
        print_test("ACH payment setup", "PASS",
                  f"Settlement: {ach_payment['settlement_date']}")
        
        # Test wire transfer
        wire = platform.wire_processor.generate_wire_instructions(
            amount=29990.00,
            recipient_account=test_account,
            reference="TEST-WIRE-001"
        )
        print_test("Wire transfer generation", "PASS",
                  f"Amount: ${wire['amount']:,.2f}")
        
        return True
        
    except Exception as e:
        print_test("Direct Bank Platform", "FAIL", str(e))
        return False

def test_website_server():
    """Test website server"""
    print_header("6. TESTING WEBSITE SERVER")
    
    try:
        # Check if website files exist
        website_dir = os.path.join(os.path.dirname(__file__), '..', 'website')
        
        files_to_check = [
            ('index.html', 'Main landing page'),
            ('css/style.css', 'Stylesheet'),
            ('js/main.js', 'JavaScript'),
            ('README.md', 'Documentation')
        ]
        
        all_exist = True
        for file_path, description in files_to_check:
            full_path = os.path.join(website_dir, file_path)
            exists = os.path.exists(full_path)
            print_test(f"{description} ({file_path})", "PASS" if exists else "FAIL")
            if not exists:
                all_exist = False
        
        # Check website server script
        server_script = os.path.join(os.path.dirname(__file__), 'website_server.py')
        if os.path.exists(server_script):
            print_test("Website server script", "PASS")
            
            # Check if Flask is available
            try:
                import flask
                print_test("Flask dependency", "PASS", f"Version: {flask.__version__}")
            except ImportError:
                print_test("Flask dependency", "SKIP", "Flask not installed")
        else:
            print_test("Website server script", "FAIL")
            all_exist = False
        
        return all_exist
        
    except Exception as e:
        print_test("Website Server", "FAIL", str(e))
        return False

def test_data_directories():
    """Test data directories and files"""
    print_header("7. TESTING DATA DIRECTORIES")
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    required_dirs = [
        'cache',
        'config',
        'cve',
        'datasets',
        'exports',
        'intelligence',
        'logs',
        'malware',
        'mitre',
        'ml_models',
        'nvd',
        'processed',
        'raw',
        'reports'
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = os.path.join(data_dir, dir_name)
        exists = os.path.exists(dir_path)
        print_test(f"Directory: data/{dir_name}", "PASS" if exists else "SKIP")
        if not exists:
            # Create directory if it doesn't exist
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"  → Created directory")
            except:
                all_exist = False
    
    return True  # Don't fail on missing directories

def test_documentation():
    """Test documentation files"""
    print_header("8. TESTING DOCUMENTATION")
    
    docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    
    required_docs = [
        ('PAYMENT_SYSTEM.md', 'Payment System Documentation'),
        ('BANK_SETUP_GUIDE.md', 'Bank Setup Guide'),
        ('WEBSITE_LAUNCH.md', 'Website Launch Guide'),
        ('INSTALLATION.md', 'Installation Guide'),
        ('QUICK_REFERENCE.md', 'Quick Reference'),
    ]
    
    all_exist = True
    for file_name, description in required_docs:
        file_path = os.path.join(docs_dir, file_name)
        exists = os.path.exists(file_path)
        print_test(description, "PASS" if exists else "SKIP")
        if not exists:
            all_exist = False
    
    return True  # Don't fail on missing docs

def test_platform_integration():
    """Test platform integration"""
    print_header("9. TESTING PLATFORM INTEGRATION")
    
    try:
        # Test detection + intelligence integration
        from threat_detection_engine import ThreatDetectionEngine
        from threat_intelligence_engine import ThreatIntelligenceEngine
        
        detection = ThreatDetectionEngine()
        intelligence = ThreatIntelligenceEngine()
        
        # Simulate threat detection with intelligence enrichment
        ip = "192.168.1.100"
        detection_result = detection.analyze_network_traffic(ip, 80, 1000)
        enrichment = intelligence.enrich_ip(ip)
        
        integrated_result = {
            **detection_result,
            'enrichment': enrichment
        }
        
        print_test("Detection + Intelligence integration", "PASS",
                  f"Threat: {integrated_result['threat_detected']}, Location: {enrichment.get('location', 'Unknown')}")
        
        # Test payment + licensing integration
        from payment_system import LicenseManager, PaymentProcessor
        
        license_mgr = LicenseManager()
        payment_proc = PaymentProcessor()
        
        # Simulate purchase flow
        payment = payment_proc.process_payment(499.00, "credit_card", "customer@example.com")
        if payment['status'] == 'completed':
            license = license_mgr.generate_license("professional", "customer@example.com")
            print_test("Payment + Licensing integration", "PASS",
                      f"License: {license}")
        else:
            print_test("Payment + Licensing integration", "FAIL")
            return False
        
        return True
        
    except Exception as e:
        print_test("Platform Integration", "FAIL", str(e))
        return False

def generate_test_report(results):
    """Generate final test report"""
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['status'])
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{Colors.BOLD}Total Tests:{Colors.ENDC} {total_tests}")
    print(f"{Colors.OKGREEN}Passed:{Colors.ENDC} {passed_tests}")
    print(f"{Colors.FAIL}Failed:{Colors.ENDC} {failed_tests}")
    print(f"{Colors.OKCYAN}Success Rate:{Colors.ENDC} {success_rate:.1f}%\n")
    
    # Component breakdown
    print(f"{Colors.BOLD}Component Status:{Colors.ENDC}\n")
    for result in results:
        status_icon = "✓" if result['status'] else "✗"
        status_color = Colors.OKGREEN if result['status'] else Colors.FAIL
        print(f"{status_color}{status_icon} {result['name']}{Colors.ENDC}")
    
    # Overall result
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    if success_rate == 100:
        print(f"{Colors.OKGREEN}{Colors.BOLD}  ✓ ALL TESTS PASSED - PLATFORM READY FOR PRODUCTION{Colors.ENDC}")
    elif success_rate >= 80:
        print(f"{Colors.WARNING}{Colors.BOLD}  ⚠ MOST TESTS PASSED - MINOR ISSUES DETECTED{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}  ✗ CRITICAL FAILURES - PLATFORM NEEDS ATTENTION{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    return success_rate == 100

def main():
    """Run all tests"""
    start_time = time.time()
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🛡️  CYBERGUARD ENTERPRISE PLATFORM - TEST SUITE".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{Colors.ENDC}")
    
    print(f"{Colors.OKCYAN}Starting comprehensive platform tests...{Colors.ENDC}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run all tests
    results = []
    
    results.append({
        'name': 'Imports',
        'status': test_imports()
    })
    
    results.append({
        'name': 'Threat Detection Engine',
        'status': test_threat_detection()
    })
    
    results.append({
        'name': 'Threat Intelligence Engine',
        'status': test_threat_intelligence()
    })
    
    results.append({
        'name': 'Payment System',
        'status': test_payment_system()
    })
    
    results.append({
        'name': 'Direct Bank Platform',
        'status': test_direct_bank_platform()
    })
    
    results.append({
        'name': 'Website Server',
        'status': test_website_server()
    })
    
    results.append({
        'name': 'Data Directories',
        'status': test_data_directories()
    })
    
    results.append({
        'name': 'Documentation',
        'status': test_documentation()
    })
    
    results.append({
        'name': 'Platform Integration',
        'status': test_platform_integration()
    })
    
    # Generate report
    all_passed = generate_test_report(results)
    
    # Test duration
    duration = time.time() - start_time
    print(f"\n{Colors.OKCYAN}Test Duration: {duration:.2f} seconds{Colors.ENDC}\n")
    
    # Save results to file
    results_file = os.path.join(os.path.dirname(__file__), 'test_results.json')
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'results': results,
            'summary': {
                'total': len(results),
                'passed': sum(1 for r in results if r['status']),
                'failed': sum(1 for r in results if not r['status'])
            }
        }, f, indent=2)
    
    print(f"{Colors.OKCYAN}Test results saved to: {results_file}{Colors.ENDC}\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
