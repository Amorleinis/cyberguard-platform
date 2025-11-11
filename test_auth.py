"""
Test Authentication System
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration"""
    print("\n🔐 Testing User Registration...")
    
    user_data = {
        "email": "john@example.com",
        "username": "johndoe",
        "password": "SecurePass123",
        "full_name": "John Doe"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json=user_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Registration successful!")
        print(f"   User ID: {data['user']['id']}")
        print(f"   Email: {data['user']['email']}")
        print(f"   Username: {data['user']['username']}")
        print(f"   Role: {data['user']['role']}")
        print(f"   Access Token: {data['access_token'][:50]}...")
        return data
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_login():
    """Test user login"""
    print("\n🔓 Testing User Login...")
    
    login_data = {
        "email": "john@example.com",
        "password": "SecurePass123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=login_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"   Access Token: {data['access_token'][:50]}...")
        print(f"   Refresh Token: {data['refresh_token'][:50]}...")
        print(f"   Expires in: {data['expires_in']} seconds")
        return data
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_get_current_user(access_token):
    """Test getting current user"""
    print("\n👤 Testing Get Current User...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/auth/me",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Successfully retrieved current user!")
        print(f"   ID: {data['id']}")
        print(f"   Email: {data['email']}")
        print(f"   Username: {data['username']}")
        print(f"   Full Name: {data['full_name']}")
        print(f"   Role: {data['role']}")
        print(f"   Subscription: {data['subscription_plan']}")
        print(f"   Active: {data['is_active']}")
        print(f"   Verified: {data['is_verified']}")
        return data
    else:
        print(f"❌ Failed to get current user: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_invalid_login():
    """Test login with invalid credentials"""
    print("\n🚫 Testing Invalid Login...")
    
    login_data = {
        "email": "wrong@example.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=login_data
    )
    
    if response.status_code == 401:
        print("✅ Invalid credentials correctly rejected!")
    else:
        print(f"❌ Unexpected response: {response.status_code}")


def main():
    print("="*60)
    print("🛡️  CYBERGUARD AUTHENTICATION TEST SUITE")
    print("="*60)
    
    # Test 1: Register new user
    reg_result = test_registration()
    if not reg_result:
        print("\n❌ Registration failed, stopping tests")
        return
    
    # Test 2: Login with registered user
    login_result = test_login()
    if not login_result:
        print("\n❌ Login failed, stopping tests")
        return
    
    # Test 3: Get current user with token
    access_token = login_result['access_token']
    test_get_current_user(access_token)
    
    # Test 4: Invalid login
    test_invalid_login()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
