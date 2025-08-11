#!/usr/bin/env python3
"""
Test various legal queries against the law firm Private GPT RAG system
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

# Comprehensive test queries organized by category
TEST_QUERIES = {
    "Billing & Fees": [
        "What are the hourly rates for Junior Associates?",
        "How much do paralegals charge per hour?",
        "What is the minimum billing increment?",
        "What happens if a client doesn't pay within 30 days?",
        "What is the initial retainer amount?",
        "When should the retainer be replenished?",
    ],
    
    "Case Law & Jurisdiction": [
        "What is the Calder v. Jones effects test?",
        "What did the Ninth Circuit decide in Mavrix Photo v. Brand Techs?",
        "How is personal jurisdiction established for internet defamation in California?",
        "What is California Civil Procedure Code section 410.10?",
        "What factors determine reasonableness of exercising jurisdiction?",
        "What is the difference between purposeful direction and purposeful availment?",
    ],
    
    "Document Preservation": [
        "What documents must be preserved during litigation hold?",
        "What are the penalties for spoliation of evidence?",
        "Can I delete emails during a legal hold?",
        "Where should I look for electronically stored information?",
        "What happens if I accidentally destroy documents under legal hold?",
        "How long does a litigation hold last?",
    ],
    
    "Settlement Terms": [
        "What are the confidentiality provisions in settlement agreements?",
        "What is the penalty for breaching settlement confidentiality?",
        "When must a plaintiff file dismissal after receiving payment?",
        "Can parties make negative statements about each other after settlement?",
        "Who bears attorneys' fees in settlement enforcement actions?",
        "What are the exceptions to settlement confidentiality?",
    ],
    
    "Client Engagement": [
        "What is included in the scope of legal representation?",
        "Does the engagement include tax advice?",
        "What are the client's responsibilities during representation?",
        "How are conflicts of interest handled?",
        "Who must approve expansion of representation scope?",
        "What costs are clients responsible for beyond attorney fees?",
    ],
    
    "Firm Administration": [
        "Who is the Director of Human Resources?",
        "Who should I contact about firm policies?",
        "Who handles attorney professional development?",
        "Who approves settlement procedures?",
        "Who oversees firm resource policies?",
        "What databases does the firm use for legal research?",
    ],
    
    "Specific Scenarios": [
        "A competitor in Nevada posted defamatory content about my California business online. Can California courts exercise jurisdiction?",
        "My retainer balance is at $4,000. What should I do?",
        "I received a litigation hold notice. Can I still use auto-delete on my emails?",
        "How much would it cost for 3 hours of Senior Partner time plus 2 hours of paralegal assistance?",
        "What should I do if opposing party violates our settlement confidentiality agreement?",
        "Can the firm represent another client in an unrelated matter while representing me?",
    ]
}

def test_query(query: str, session_id: str = "test_session") -> dict:
    """Send a query to the RAG system and return the response"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": query, "session_id": session_id},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "content": response.text}
            
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "content": None}

def main():
    print("=" * 80)
    print(" LAW FIRM PRIVATE GPT - COMPREHENSIVE QUERY TEST ")
    print("=" * 80)
    print()
    
    total_queries = sum(len(queries) for queries in TEST_QUERIES.values())
    print(f"Testing {total_queries} queries across {len(TEST_QUERIES)} categories\n")
    
    # Test each category
    for category, queries in TEST_QUERIES.items():
        print(f"\n{'='*60}")
        print(f" {category.upper()} ")
        print(f"{'='*60}\n")
        
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. QUERY: {query}")
            print("-" * 40)
            
            # Send query
            result = test_query(query, session_id=f"test_{category.replace(' ', '_').lower()}")
            
            if "error" in result:
                print(f"❌ ERROR: {result['error']}")
            else:
                response = result.get("content", "No response")
                
                # Truncate long responses for display
                if len(response) > 300:
                    response = response[:300] + "..."
                    
                print(f"✅ RESPONSE: {response}")
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.5)
    
    print("\n" + "=" * 80)
    print(" TEST COMPLETE ")
    print("=" * 80)
    
    # Bonus: Test the system status endpoint
    print("\n📊 Checking System Status...")
    try:
        status_response = requests.get(f"{BASE_URL}/api/rag/status")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"✅ System Status: {status.get('status', 'Unknown')}")
            if "configuration" in status:
                config = status["configuration"]
                print(f"   - Chunk Size: {config['chunking']['chunk_size']}")
                print(f"   - Similarity Threshold: {config['similarity_threshold']}")
                print(f"   - Max Context Length: {config['max_context_length']}")
        else:
            print(f"❌ Could not get system status: HTTP {status_response.status_code}")
    except Exception as e:
        print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    main()
