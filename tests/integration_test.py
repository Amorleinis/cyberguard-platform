"""
CyberGuard Platform Integration Tests
Tests all platform components and their integration
"""

import requests
import json
import time
import websocket
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
WEB_URL = "http://localhost:3000"
WS_URL = "ws://localhost:8000"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_test(name, status, details=""):
    symbol = "✓" if status else "✗"
    color = GREEN if status else RED
    print(f"{color}{symbol}{RESET} {name}")
    if details:
        print(f"  {YELLOW}{details}{RESET}")

def test_backend_api():
    """Test Backend API endpoints"""
    print_header("BACKEND API TESTS")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health check
    tests_total += 1
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        success = response.status_code == 200
        print_test("Health Check", success, f"Status: {response.status_code}")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Health Check", False, f"Error: {e}")
    
    # Test 2: Dashboard endpoint
    tests_total += 1
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/dashboard", timeout=5)
        success = response.status_code == 200
        data = response.json() if success else {}
        
        # Verify data structure
        has_metrics = all(key in data for key in ['active_threats', 'cpu_usage', 'memory_usage'])
        success = success and has_metrics
        
        print_test("Dashboard Endpoint", success, 
                  f"Active Threats: {data.get('active_threats', 'N/A')}, "
                  f"CPU: {data.get('cpu_usage', 'N/A')}%, "
                  f"Memory: {data.get('memory_usage', 'N/A')}%")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Dashboard Endpoint", False, f"Error: {e}")
    
    # Test 3: Threats endpoint
    tests_total += 1
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/threats?limit=5", timeout=5)
        success = response.status_code == 200
        data = response.json() if success else {}
        threat_count = len(data.get('threats', []))
        
        print_test("Threats Endpoint", success, 
                  f"Retrieved {threat_count} threats")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Threats Endpoint", False, f"Error: {e}")
    
    # Test 4: Threat stats endpoint
    tests_total += 1
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/threats/stats", timeout=5)
        success = response.status_code == 200
        data = response.json() if success else {}
        
        print_test("Threat Stats", success, 
                  f"Total: {data.get('total_threats', 'N/A')}, "
                  f"Detection Rate: {data.get('detection_rate', 'N/A')}%")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Threat Stats", False, f"Error: {e}")
    
    # Test 5: Authentication endpoints
    tests_total += 1
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            params={"email": "test@example.com", "password": "password"},
            timeout=5
        )
        success = response.status_code == 200
        data = response.json() if success else {}
        
        print_test("Login Endpoint", success, 
                  f"Token received: {bool(data.get('access_token'))}")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Login Endpoint", False, f"Error: {e}")
    
    # Test 6: API Documentation
    tests_total += 1
    try:
        response = requests.get(f"{BACKEND_URL}/api/docs", timeout=5)
        success = response.status_code == 200
        print_test("API Documentation", success, f"Swagger UI accessible")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("API Documentation", False, f"Error: {e}")
    
    print(f"\n{BLUE}Backend API: {tests_passed}/{tests_total} tests passed{RESET}")
    return tests_passed, tests_total

def test_websocket():
    """Test WebSocket real-time updates"""
    print_header("WEBSOCKET TESTS")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: WebSocket connection
    tests_total += 1
    try:
        ws = websocket.create_connection(f"{WS_URL}/ws/threats", timeout=10)
        print_test("WebSocket Connection", True, "Connected successfully")
        tests_passed += 1
        
        # Test 2: Receive threat updates
        tests_total += 1
        print(f"{YELLOW}  Waiting for threat updates (10 seconds)...{RESET}")
        
        messages_received = 0
        start_time = time.time()
        
        while time.time() - start_time < 10:
            try:
                message = ws.recv()
                data = json.loads(message)
                messages_received += 1
                
                if data.get('type') == 'threat':
                    threat = data.get('threat', {})
                    print(f"  {GREEN}→{RESET} Threat: {threat.get('type')} "
                          f"({threat.get('severity')}) from {threat.get('source_ip')}")
                elif data.get('type') == 'connection':
                    print(f"  {BLUE}→{RESET} {data.get('message')}")
                    
            except Exception as e:
                if "timed out" not in str(e):
                    print(f"  {RED}Error receiving: {e}{RESET}")
                break
        
        ws.close()
        
        success = messages_received > 0
        print_test("Threat Updates", success, 
                  f"Received {messages_received} messages in 10 seconds")
        if success:
            tests_passed += 1
            
    except Exception as e:
        print_test("WebSocket Connection", False, f"Error: {e}")
        tests_total += 1  # Count the receive test as well
    
    print(f"\n{BLUE}WebSocket: {tests_passed}/{tests_total} tests passed{RESET}")
    return tests_passed, tests_total

def test_web_app():
    """Test Web Application"""
    print_header("WEB APPLICATION TESTS")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Web server is running
    tests_total += 1
    try:
        response = requests.get(WEB_URL, timeout=5)
        success = response.status_code == 200
        print_test("Web Server", success, f"Status: {response.status_code}")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Web Server", False, f"Error: {e}")
    
    # Test 2: Static files accessible
    tests_total += 1
    try:
        css = requests.get(f"{WEB_URL}/styles.css", timeout=5)
        js = requests.get(f"{WEB_URL}/app.js", timeout=5)
        success = css.status_code == 200 and js.status_code == 200
        print_test("Static Files", success, 
                  f"CSS: {css.status_code}, JS: {js.status_code}")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Static Files", False, f"Error: {e}")
    
    # Test 3: HTML structure
    tests_total += 1
    try:
        response = requests.get(WEB_URL, timeout=5)
        html = response.text
        
        required_elements = [
            'CyberGuard',
            'Dashboard',
            'Threats',
            'Protection',
            'Settings'
        ]
        
        success = all(elem in html for elem in required_elements)
        print_test("HTML Structure", success, 
                  f"Contains required elements: {success}")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("HTML Structure", False, f"Error: {e}")
    
    print(f"\n{BLUE}Web Application: {tests_passed}/{tests_total} tests passed{RESET}")
    return tests_passed, tests_total

def test_integration():
    """Test end-to-end integration"""
    print_header("INTEGRATION TESTS")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Backend → Web data flow
    tests_total += 1
    try:
        # Get data from backend
        backend_data = requests.get(f"{BACKEND_URL}/api/v1/dashboard", timeout=5).json()
        
        # Verify the web app can consume this data structure
        success = all(key in backend_data for key in ['active_threats', 'blocked_threats'])
        
        print_test("Backend → Web Data Flow", success, 
                  f"Data structure compatible: {success}")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("Backend → Web Data Flow", False, f"Error: {e}")
    
    # Test 2: Real-time update flow
    tests_total += 1
    try:
        print(f"{YELLOW}  Testing real-time threat updates...{RESET}")
        
        ws = websocket.create_connection(f"{WS_URL}/ws/threats", timeout=10)
        
        # Wait for a threat update
        received_threat = False
        start_time = time.time()
        
        while time.time() - start_time < 12:
            try:
                message = ws.recv()
                data = json.loads(message)
                
                if data.get('type') == 'threat':
                    received_threat = True
                    threat = data.get('threat', {})
                    print(f"  {GREEN}→{RESET} Real-time threat: {threat.get('type')}")
                    break
            except:
                break
        
        ws.close()
        
        print_test("Real-time Updates", received_threat, 
                  f"Threat received via WebSocket: {received_threat}")
        if received_threat:
            tests_passed += 1
    except Exception as e:
        print_test("Real-time Updates", False, f"Error: {e}")
    
    # Test 3: CORS configuration
    tests_total += 1
    try:
        response = requests.options(f"{BACKEND_URL}/api/v1/dashboard", 
                                    headers={'Origin': WEB_URL}, 
                                    timeout=5)
        success = response.status_code in [200, 204]
        print_test("CORS Configuration", success, 
                  f"Cross-origin requests allowed: {success}")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("CORS Configuration", False, f"Error: {e}")
    
    print(f"\n{BLUE}Integration: {tests_passed}/{tests_total} tests passed{RESET}")
    return tests_passed, tests_total

def main():
    """Run all integration tests"""
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}{'CyberGuard Platform Integration Tests':^60}{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"\n{YELLOW}Testing platform components...{RESET}\n")
    
    total_passed = 0
    total_tests = 0
    
    # Run all test suites
    backend_passed, backend_total = test_backend_api()
    total_passed += backend_passed
    total_tests += backend_total
    
    ws_passed, ws_total = test_websocket()
    total_passed += ws_passed
    total_tests += ws_total
    
    web_passed, web_total = test_web_app()
    total_passed += web_passed
    total_tests += web_total
    
    int_passed, int_total = test_integration()
    total_passed += int_passed
    total_tests += int_total
    
    # Final summary
    print_header("TEST SUMMARY")
    
    percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {GREEN}{total_passed}{RESET}")
    print(f"Failed: {RED}{total_tests - total_passed}{RESET}")
    print(f"Success Rate: {GREEN if percentage >= 80 else RED}{percentage:.1f}%{RESET}")
    
    if percentage >= 80:
        print(f"\n{GREEN}✓ Platform integration successful!{RESET}")
    else:
        print(f"\n{RED}✗ Some tests failed. Review errors above.{RESET}")
    
    print(f"\n{BLUE}{'='*60}{RESET}\n")

if __name__ == "__main__":
    main()
