#!/usr/bin/env python3

import requests

def simple_test():
    try:
        print("Testing backend directly...")
        response = requests.get("https://yourstock.ai/backend/", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content (first 200 chars): {response.text[:200]}")
        
        if response.status_code == 500:
            print("\n🔍 This is a 500 error - the server is trying to run Python but failing")
            print("Most likely causes:")
            print("1. Virtual environment path is wrong")
            print("2. Dependencies not installed in the right place")
            print("3. Import errors in the Python code")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simple_test() 