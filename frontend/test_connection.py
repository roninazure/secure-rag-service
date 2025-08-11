#!/usr/bin/env python3
"""
Test script to verify API connection
"""

import requests
import json

def test_api():
    url = "http://localhost:8000/api/chat/"
    
    # Test data
    payload = {
        "message": "What are the billing rates for Senior Partners?"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:5173"  # Simulate browser origin
    }
    
    print("Testing API connection...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 50)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server at http://localhost:8000")
        print("Make sure the backend is running: cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
