#!/usr/bin/env python3
"""
API Test Script for Authentication
Test the login/signup endpoints
"""

import requests
import json

# API base URL (adjust as needed)
BASE_URL = "http://localhost:5000/api"

def test_signup():
    """Test user registration"""
    print("\n📝 Testing Signup")
    print("-" * 20)
    
    signup_data = {
        "name": "API Test User",
        "email": "apitest@example.com",
        "password": "apitest123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Signup successful!")
            print(f"   User ID: {data['user']['id']}")
            print(f"   Token: {data['token'][:50]}...")
            return data['token']
        else:
            print(f"❌ Signup failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return None

def test_signin():
    """Test user login"""
    print("\n🔑 Testing Signin")
    print("-" * 20)
    
    signin_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signin", json=signin_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Signin successful!")
            print(f"   User: {data['user']['name']} ({data['user']['email']})")
            print(f"   Token: {data['token'][:50]}...")
            return data['token']
        else:
            print(f"❌ Signin failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Signin error: {e}")
        return None

def test_verify_auth(token):
    """Test token verification"""
    print("\n🔍 Testing Token Verification")
    print("-" * 20)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Token verification successful!")
            print(f"   User ID: {data['user']['user_id']}")
            print(f"   Email: {data['user']['email']}")
        else:
            print(f"❌ Token verification failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Verification error: {e}")

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    print("\n🛡️ Testing Protected Endpoint")
    print("-" * 20)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test with a protected endpoint (you can change this to any protected endpoint)
        response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Protected endpoint access successful!")
        else:
            print(f"❌ Protected endpoint access failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Protected endpoint error: {e}")

if __name__ == "__main__":
    print("🚀 API Authentication Tests")
    print("=" * 50)
    
    # Test signin (using existing user)
    token = test_signin()
    
    if token:
        # Test token verification
        test_verify_auth(token)
        
        # Test protected endpoint
        test_protected_endpoint(token)
    
    # Test signup (creates new user)
    new_token = test_signup()
    
    if new_token:
        test_verify_auth(new_token)
    
    print("\n✅ API tests completed!")
