#!/usr/bin/env python3
"""
Authentication Database Initialization Script
This script initializes the auth database and tests the login functionality
"""

import sqlite3
import bcrypt
import os
import sys
from datetime import datetime

# Add the parent directory to the path to import from backend_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def init_auth_database():
    """Initialize the authentication database"""
    print("🔐 Initializing Authentication Database")
    print("=" * 50)
    
    # Database path
    AUTH_DB_PATH = os.path.join(os.path.dirname(__file__), 'auth.db')
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(AUTH_DB_PATH), exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(AUTH_DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            google_id TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("✅ Users table created successfully")
    
    # Test users for development
    test_users = [
        {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        },
        {
            'name': 'Demo User',
            'email': 'user@test.com',
            'password': 'testpass123'
        },
        {
            'name': 'Admin User',
            'email': 'demo@marketsentiment.ai',
            'password': 'demo123'
        },
        {
            'name': 'John Trader',
            'email': 'john@trader.com',
            'password': 'trading123'
        }
    ]
    
    print("\n👥 Adding Test Users")
    print("-" * 30)
    
    for user in test_users:
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (user['email'],))
        if not cursor.fetchone():
            # Hash the password
            password_hash = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
            ''', (user['name'], user['email'], password_hash.decode('utf-8')))
            print(f"✅ Added user: {user['name']} ({user['email']})")
        else:
            print(f"⏭️  User already exists: {user['name']} ({user['email']})")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Authentication database initialized successfully!")

def test_login_functionality():
    """Test the login functionality"""
    print("\n🧪 Testing Login Functionality")
    print("=" * 50)
    
    AUTH_DB_PATH = os.path.join(os.path.dirname(__file__), 'auth.db')
    conn = sqlite3.connect(AUTH_DB_PATH)
    cursor = conn.cursor()
    
    # Test cases
    test_cases = [
        {
            'email': 'test@example.com',
            'password': 'password123',
            'expected': 'success'
        },
        {
            'email': 'user@test.com',
            'password': 'testpass123',
            'expected': 'success'
        },
        {
            'email': 'demo@marketsentiment.ai',
            'password': 'demo123',
            'expected': 'success'
        },
        {
            'email': 'john@trader.com',
            'password': 'trading123',
            'expected': 'success'
        },
        {
            'email': 'wrong@email.com',
            'password': 'password123',
            'expected': 'fail'
        },
        {
            'email': 'test@example.com',
            'password': 'wrongpassword',
            'expected': 'fail'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['email']}")
        print("-" * 20)
        
        try:
            # Get user by email
            cursor.execute('SELECT id, name, email, password_hash FROM users WHERE email = ?', 
                         (test_case['email'],))
            user = cursor.fetchone()
            
            if not user:
                if test_case['expected'] == 'fail':
                    print("✅ Correctly rejected: User not found")
                else:
                    print("❌ Unexpected failure: User not found")
                continue
            
            user_id, name, email, password_hash = user
            
            # Verify password
            if bcrypt.checkpw(test_case['password'].encode('utf-8'), password_hash.encode('utf-8')):
                if test_case['expected'] == 'success':
                    print(f"✅ Login successful: {name} ({email})")
                    print(f"   User ID: {user_id}")
                else:
                    print("❌ Unexpected success: Should have failed")
            else:
                if test_case['expected'] == 'fail':
                    print("✅ Correctly rejected: Invalid password")
                else:
                    print("❌ Unexpected failure: Invalid password")
                    
        except Exception as e:
            print(f"❌ Test error: {e}")
    
    conn.close()

def show_database_status():
    """Show the current status of the authentication database"""
    print("\n📊 Database Status")
    print("=" * 50)
    
    AUTH_DB_PATH = os.path.join(os.path.dirname(__file__), 'auth.db')
    
    if not os.path.exists(AUTH_DB_PATH):
        print("❌ Database file does not exist")
        return
    
    conn = sqlite3.connect(AUTH_DB_PATH)
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone():
        print("✅ Users table exists")
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📈 Total users: {user_count}")
        
        # Show all users (without passwords)
        cursor.execute("SELECT id, name, email, created_at FROM users ORDER BY id")
        users = cursor.fetchall()
        
        print("\n👥 Registered Users:")
        print("-" * 30)
        for user in users:
            user_id, name, email, created_at = user
            print(f"   ID: {user_id} | {name} | {email} | Created: {created_at}")
    else:
        print("❌ Users table does not exist")
    
    conn.close()

def create_api_test_script():
    """Create a script to test the API endpoints"""
    print("\n🌐 Creating API Test Script")
    print("=" * 50)
    
    test_script = '''#!/usr/bin/env python3
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
    print("\\n📝 Testing Signup")
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
    print("\\n🔑 Testing Signin")
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
    print("\\n🔍 Testing Token Verification")
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
    print("\\n🛡️ Testing Protected Endpoint")
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
    
    print("\\n✅ API tests completed!")
'''
    
    with open('db/test_auth_api.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created test_auth_api.py")

def main():
    """Main function to run all initialization steps"""
    print("🚀 Authentication System Setup")
    print("=" * 60)
    
    # Initialize database
    init_auth_database()
    
    # Show database status
    show_database_status()
    
    # Test login functionality
    test_login_functionality()
    
    # Create API test script
    create_api_test_script()
    
    print("\n🎉 Authentication System Setup Complete!")
    print("=" * 60)
    print("📁 Database: db/auth.db")
    print("🧪 Test Script: db/test_auth_api.py")
    print("🌐 API Endpoints:")
    print("   POST /api/auth/signup - User registration")
    print("   POST /api/auth/signin - User login")
    print("   GET  /api/auth/verify - Verify token")
    print("   POST /api/auth/logout - User logout")
    print("\n💡 Next Steps:")
    print("   1. Start your backend server")
    print("   2. Run: python db/test_auth_api.py")
    print("   3. Test login in your frontend")

if __name__ == "__main__":
    main() 