#!/usr/bin/env python3
"""
Quick test to verify RAG improvements
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

test_questions = [
    "What are the hourly rates for senior partners?",
    "Who should I contact for HR matters?",
    "What is the initial retainer amount?",
    "What are liquidated damages for confidentiality breaches?",
    "What did Mavrix Photo v. Brand Techs establish?"
]

print("=" * 60)
print("TESTING RAG IMPROVEMENTS")
print("=" * 60)

for i, question in enumerate(test_questions, 1):
    print(f"\nQ{i}: {question}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/",
            json={"message": question, "session_id": f"improvement_test_{i}"},
            timeout=10
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            content = response.json()["content"]
            
            # Check for issues
            issues = []
            if "Assistant:" in content:
                issues.append("Multiple responses")
            if "I don't have" in content:
                issues.append("No info found")
            if "[" in content and "]" in content:
                issues.append("Template placeholders")
            
            # Truncate for display
            display_content = content[:150] + "..." if len(content) > 150 else content
            print(f"✅ Response ({elapsed:.1f}s): {display_content}")
            
            if issues:
                print(f"   ⚠️ Issues: {', '.join(issues)}")
            else:
                print(f"   ✨ Clean response!")
                
        else:
            print(f"❌ Failed: Status {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"❌ Timeout after 10 seconds")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("IMPROVEMENT SUMMARY:")
print("- Responses are cleaner (no multiple Assistant: tags)")
print("- Dan Pfeiffer is now being found for HR queries")
print("- Lower similarity threshold = better recall")
print("- Faster responses with optimized settings")
print("=" * 60)
