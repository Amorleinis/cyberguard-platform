"""
Test authentication and database integration
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def print_result(test_name, response):
    """Print test result"""
    status_color = "\033[92m" if response.status_code < 400 else "\033[91m"
    print(f"\n{status_color}[{response.status_code}] {test_name}\033[0m")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_auth():
    """Test authentication endpoints"""
    print("\n" + "="*60)
    print("Testing CyberGuard Authentication & Database")
    print("="*60)
    
    # Test 1: Login with admin
    print("\n\n1️⃣  Testing admin login...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "admin@cyberguard.com",
            "password": "admin123"
        }
    )
    print_result("Admin Login", response)
    
    if response.status_code == 200:
        admin_token = response.json()["access_token"]
        
        # Test 2: Get current user
        print("\n\n2️⃣  Testing /auth/me endpoint...")
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print_result("Get Current User", response)
        
        # Test 3: Get threats stats
        print("\n\n3️⃣  Testing /threats/stats endpoint...")
        response = requests.get(
            f"{BASE_URL}/threats/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print_result("Threat Statistics", response)
        
        # Test 4: Get threats list
        print("\n\n4️⃣  Testing /threats endpoint...")
        response = requests.get(
            f"{BASE_URL}/threats?limit=5",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print_result("Threat List", response)
        
        # Test 5: Create new threat
        print("\n\n5️⃣  Testing threat creation...")
        response = requests.post(
            f"{BASE_URL}/threats/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "threat_type": "ransomware",
                "severity": "critical",
                "status": "active",
                "source_ip": "192.168.1.100",
                "description": "Ransomware detected via API test"
            }
        )
        print_result("Create Threat", response)
        
        # Test 6: Get users (admin only)
        print("\n\n6️⃣  Testing /users endpoint (admin only)...")
        response = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print_result("List Users", response)
    
    # Test 7: Register new user
    print("\n\n7️⃣  Testing user registration...")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "newuser@test.com",
            "username": "newuser",
            "full_name": "New Test User",
            "password": "testpass123"
        }
    )
    print_result("Register New User", response)
    
    if response.status_code == 201:
        # Test 8: Login with new user
        print("\n\n8️⃣  Testing new user login...")
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": "newuser@test.com",
                "password": "testpass123"
            }
        )
        print_result("New User Login", response)
        
        if response.status_code == 200:
            new_user_token = response.json()["access_token"]
            
            # Test 9: Try to access users (should fail - not admin)
            print("\n\n9️⃣  Testing authorization (should fail)...")
            response = requests.get(
                f"{BASE_URL}/users/",
                headers={"Authorization": f"Bearer {new_user_token}"}
            )
            print_result("Non-Admin Trying to List Users", response)
    
    # Test 10: Test invalid login
    print("\n\n🔟 Testing invalid credentials...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "wrong@email.com",
            "password": "wrongpass"
        }
    )
    print_result("Invalid Login", response)
    
    print("\n\n" + "="*60)
    print("Authentication Testing Complete! ✅")
    print("="*60)

if __name__ == "__main__":
    test_auth()
