#!/usr/bin/env python3
"""
Comprehensive chat test script for AWS Private GPT deployment
Tests various query types against the knowledge base
"""
import requests
import json
import time
from datetime import datetime

# AWS EC2 endpoint
API_URL = "http://3.87.201.201:8000/api"

# Test queries covering different aspects of the knowledge base
TEST_QUERIES = [
    # Basic firm info
    ("Where are your offices located?", "office location"),
    ("What practice areas does the firm specialize in?", "practice areas"),
    ("Tell me about your litigation practice", "litigation"),
    ("What corporate services do you offer?", "corporate services"),
    
    # Billing and financial
    ("What is the retainer amount for new clients?", "retainer"),
    ("How does billing work?", "billing"),
    ("What are your payment terms?", "payment"),
    
    # HR and policies
    ("What is the PTO policy?", "PTO policy"),
    ("Who approves time off requests?", "Dan Pfeiffer"),
    ("What is the remote work policy?", "remote work"),
    
    # Client service
    ("What is your approach to client service?", "client philosophy"),
    ("How do you handle client communications?", "communication"),
]

def test_chat(query, expected_keywords):
    """Send a chat query and check response"""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"Expected keywords: {expected_keywords}")
    print('-'*60)
    
    # Create a new session for each test to avoid context pollution
    session_id = f"test_{int(time.time())}_{hash(query)}"
    
    payload = {
        "message": query,
        "session_id": session_id
    }
    
    try:
        response = requests.post(
            f"{API_URL}/chat/",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', '')
            
            # Check for quality indicators
            has_keywords = expected_keywords.lower() in content.lower()
            has_dont_have = "don't have" in content.lower() or "do not have" in content.lower()
            is_greeting = any(greet in content.lower() for greet in ['hello', 'hi!', 'welcome', 'how can i help'])
            
            print(f"Status: ✓ Success")
            print(f"Keywords found: {'✓' if has_keywords else '✗'}")
            print(f"Has 'don't have': {'✗ (bad)' if has_dont_have else '✓ (good)'}")
            print(f"Generic greeting: {'✗ (bad)' if is_greeting else '✓ (good)'}")
            print(f"\nResponse preview (first 300 chars):")
            print(content[:300] + "..." if len(content) > 300 else content)
            
            return {
                'success': True,
                'has_keywords': has_keywords,
                'has_dont_have': has_dont_have,
                'is_greeting': is_greeting,
                'response': content
            }
        else:
            print(f"Status: ✗ Error {response.status_code}")
            print(f"Response: {response.text}")
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        print(f"Status: ✗ Exception")
        print(f"Error: {e}")
        return {'success': False, 'error': str(e)}

def run_all_tests():
    """Run all test queries and summarize results"""
    print(f"\n{'#'*60}")
    print(f"AWS Private GPT Chat Test Suite")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Endpoint: {API_URL}")
    print(f"{'#'*60}")
    
    # First, check if API is up
    print("\nChecking API health...")
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✓ API is healthy")
        else:
            print(f"⚠ API returned status {health_response.status_code}")
    except Exception as e:
        print(f"✗ Cannot reach API: {e}")
        return
    
    # Run all tests
    results = []
    for query, keywords in TEST_QUERIES:
        result = test_chat(query, keywords)
        results.append(result)
        time.sleep(1)  # Small delay between requests
    
    # Summarize results
    print(f"\n{'#'*60}")
    print("TEST SUMMARY")
    print(f"{'#'*60}")
    
    total = len(results)
    successful = sum(1 for r in results if r.get('success'))
    with_keywords = sum(1 for r in results if r.get('has_keywords'))
    without_dont_have = sum(1 for r in results if not r.get('has_dont_have'))
    without_greeting = sum(1 for r in results if not r.get('is_greeting'))
    
    print(f"\nTotal tests: {total}")
    print(f"Successful API calls: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"Responses with expected keywords: {with_keywords}/{successful} ({with_keywords/max(successful,1)*100:.1f}%)")
    print(f"Responses without 'don't have': {without_dont_have}/{successful} ({without_dont_have/max(successful,1)*100:.1f}%)")
    print(f"Responses without generic greeting: {without_greeting}/{successful} ({without_greeting/max(successful,1)*100:.1f}%)")
    
    quality_score = (with_keywords + without_dont_have + without_greeting) / (3 * max(successful, 1)) * 100
    print(f"\nOverall Quality Score: {quality_score:.1f}%")
    
    if quality_score >= 80:
        print("✓ System is performing well!")
    elif quality_score >= 60:
        print("⚠ System needs some tuning")
    else:
        print("✗ System has significant issues")
    
    return results

if __name__ == "__main__":
    results = run_all_tests()
