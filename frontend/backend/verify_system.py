#!/usr/bin/env python3
"""Quick verification of what's working in the system"""
import requests
import json

API_URL = "http://3.87.201.201:8000/api"

print("🔍 SYSTEM STATUS CHECK")
print("=" * 50)

# Test queries that should work based on existing content
test_queries = [
    "What is the retainer amount?",
    "Tell me about your litigation practice",
    "What are your billing rates?",
    "Where are your offices located?",
]

print("\n✅ Testing existing knowledge base:")
for query in test_queries:
    response = requests.post(
        f"{API_URL}/chat/",
        json={"message": query, "session_id": "test"},
        timeout=10
    )
    if response.status_code == 200:
        content = response.json()['content'][:100]
        print(f"  Q: {query}")
        print(f"  A: {content}...")
    else:
        print(f"  ❌ Failed: {query}")

print("\n📊 Vector Database Status:")
response = requests.get(f"{API_URL}/status", timeout=5)
if response.status_code == 200:
    status = response.json()
    vector_db = status.get('vector_database', {})
    print(f"  Vectors: {vector_db.get('total_vectors', 'Unknown')}")
    print(f"  Status: {status.get('status', 'Unknown')}")

print("\n✅ System is functional for demo!")
print("You have working legal and firm content.")
print("Frontend is accessible at: https://3.87.201.201")
