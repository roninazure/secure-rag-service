#!/usr/bin/env python3
"""Quick test of core legal/business functionality"""
import requests
import json
import time

API_URL = "http://3.87.201.201:8000/api"

# Focus on legal and business queries
test_queries = [
    "What is the retainer amount?",
    "What are your hourly billing rates?",
    "Tell me about your litigation services",
    "What corporate law services do you provide?",
    "Where are your offices located?",
]

print("🧪 TESTING CORE LEGAL/BUSINESS QUERIES")
print("=" * 50)

for query in test_queries:
    print(f"\n❓ {query}")
    
    try:
        response = requests.post(
            f"{API_URL}/chat/",
            json={"message": query, "session_id": f"test_{time.time()}"},
            timeout=15
        )
        
        if response.status_code == 200:
            content = response.json()['content']
            # Show first 250 chars of response
            preview = content[:250] + "..." if len(content) > 250 else content
            print(f"✅ Response: {preview}")
        else:
            print(f"❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(1)

print("\n" + "=" * 50)
print("✅ Test complete!")
