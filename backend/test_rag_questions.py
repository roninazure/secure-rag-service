#!/usr/bin/env python3
"""
Comprehensive RAG System Testing
Tests various question types to evaluate retrieval quality and response accuracy
"""

import requests
import json
from datetime import datetime
from typing import List, Dict

BASE_URL = "http://localhost:8000"

# Test questions organized by category
TEST_QUESTIONS = {
    "Billing & Rates": [
        "What are the hourly rates for senior partners?",
        "How much is the initial retainer for new clients?",
        "What expenses are clients responsible for beyond hourly fees?",
        "What is the billing increment for time tracking?",
    ],
    
    "HR & Policies": [
        "Who handles HR matters at the firm?",
        "What is the remote work policy?",
        "How many CLE hours are required annually?",
        "What is the professional development reimbursement amount?",
    ],
    
    "Legal Procedures": [
        "What documents must be preserved during a litigation hold?",
        "What are the consequences of not preserving documents?",
        "What is included in the scope of legal representation?",
        "What are liquidated damages for confidentiality breaches?",
    ],
    
    "Case Law & Research": [
        "What did Mavrix Photo v. Brand Techs establish?",
        "How does the Calder effects test work?",
        "What are the three prongs for specific jurisdiction?",
        "What factors determine reasonableness of jurisdiction?",
    ],
    
    "Complex Queries": [
        "Compare the billing rates for all attorney levels and explain the retainer process",
        "What are all the forms of documents that need to be preserved and where might they be stored?",
        "Explain the complete process for establishing personal jurisdiction in internet defamation cases",
        "What are the client's responsibilities in an engagement and what happens if they don't pay?",
    ]
}

def test_question(question: str, session_id: str = "test") -> Dict:
    """Send a question to the RAG system and return the response"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/",
            json={"message": question, "session_id": session_id},
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "response": response.json(),
                "latency": response.elapsed.total_seconds()
            }
        else:
            return {
                "success": False,
                "error": f"Status {response.status_code}: {response.text}",
                "latency": response.elapsed.total_seconds()
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "latency": 0
        }

def analyze_response(question: str, response: Dict, expected_keywords: List[str] = None) -> Dict:
    """Analyze the quality of a response"""
    analysis = {
        "question": question,
        "response_length": 0,
        "latency": response.get("latency", 0),
        "has_answer": False,
        "keywords_found": [],
        "issues": []
    }
    
    if response["success"]:
        content = response["response"].get("content", "")
        analysis["response_length"] = len(content)
        analysis["has_answer"] = len(content) > 50
        
        # Check for common issues
        if "I don't have" in content or "I cannot" in content:
            analysis["issues"].append("Admission of lack of knowledge")
        
        if "[" in content and "]" in content:
            analysis["issues"].append("Contains template placeholders")
            
        if "Assistant:" in content:
            analysis["issues"].append("Multiple assistant responses concatenated")
        
        # Check for expected keywords if provided
        if expected_keywords:
            content_lower = content.lower()
            for keyword in expected_keywords:
                if keyword.lower() in content_lower:
                    analysis["keywords_found"].append(keyword)
    else:
        analysis["issues"].append(f"Request failed: {response.get('error', 'Unknown error')}")
    
    return analysis

def run_comprehensive_test():
    """Run all test questions and generate a report"""
    print("=" * 80)
    print("RAG SYSTEM COMPREHENSIVE TEST")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    all_results = {}
    total_questions = 0
    successful_responses = 0
    total_latency = 0
    
    for category, questions in TEST_QUESTIONS.items():
        print(f"\n📚 Testing Category: {category}")
        print("-" * 40)
        
        category_results = []
        
        for i, question in enumerate(questions, 1):
            print(f"\n❓ Q{i}: {question[:80]}...")
            
            # Send question
            response = test_question(question, session_id=f"{category}_{i}")
            
            # Define expected keywords based on question
            expected = []
            if "rate" in question.lower():
                expected = ["$", "hour", "750", "550", "450", "350"]
            elif "retainer" in question.lower():
                expected = ["$25,000", "25000", "retainer", "trust account"]
            elif "pfeiffer" in question.lower() or "hr" in question.lower():
                expected = ["Dan Pfeiffer", "Human Resources", "HR"]
            elif "mavrix" in question.lower():
                expected = ["Mavrix", "jurisdiction", "website", "something more"]
            elif "litigation hold" in question.lower():
                expected = ["preserve", "documents", "emails", "suspension"]
            
            # Analyze response
            analysis = analyze_response(question, response, expected)
            category_results.append(analysis)
            
            # Update statistics
            total_questions += 1
            if response["success"]:
                successful_responses += 1
                total_latency += response["latency"]
                
                # Print response preview
                content = response["response"].get("content", "")[:200]
                if len(response["response"].get("content", "")) > 200:
                    content += "..."
                print(f"✅ Response: {content}")
                
                # Print analysis
                if analysis["keywords_found"]:
                    print(f"   Keywords found: {', '.join(analysis['keywords_found'])}")
                if analysis["issues"]:
                    print(f"   ⚠️ Issues: {', '.join(analysis['issues'])}")
                print(f"   Latency: {analysis['latency']:.2f}s")
            else:
                print(f"❌ Failed: {response.get('error', 'Unknown error')}")
        
        all_results[category] = category_results
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("TEST SUMMARY REPORT")
    print("=" * 80)
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total Questions: {total_questions}")
    print(f"   Successful Responses: {successful_responses}/{total_questions} ({successful_responses/total_questions*100:.1f}%)")
    if successful_responses > 0:
        print(f"   Average Latency: {total_latency/successful_responses:.2f}s")
    
    print(f"\n📈 Category Performance:")
    for category, results in all_results.items():
        success_count = sum(1 for r in results if r["has_answer"])
        keyword_accuracy = []
        for r in results:
            if r.get("keywords_found"):
                keyword_accuracy.append(len(r["keywords_found"]))
        
        print(f"\n   {category}:")
        print(f"      Questions with answers: {success_count}/{len(results)}")
        if keyword_accuracy:
            print(f"      Avg keywords found: {sum(keyword_accuracy)/len(keyword_accuracy):.1f}")
        
        # Common issues in category
        all_issues = []
        for r in results:
            all_issues.extend(r.get("issues", []))
        if all_issues:
            unique_issues = list(set(all_issues))
            print(f"      Common issues: {', '.join(unique_issues[:3])}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations = []
    
    # Check for specific issues
    template_issues = sum(1 for cat_results in all_results.values() 
                         for r in cat_results 
                         if "template placeholders" in r.get("issues", []))
    if template_issues > 2:
        recommendations.append("• Replace template placeholders with example values in documents")
    
    hallucination_issues = sum(1 for cat_results in all_results.values() 
                              for r in cat_results 
                              if not r.get("keywords_found", []))
    if hallucination_issues > 5:
        recommendations.append("• Consider using Claude or GPT-4 for better factual accuracy")
    
    if total_latency/successful_responses > 3:
        recommendations.append("• Optimize chunk size or reduce top_k for faster responses")
    
    recommendations.append("• Add more specific firm documents to improve coverage")
    recommendations.append("• Implement document versioning for templates")
    recommendations.append("• Add citation tracking to show source documents")
    
    for rec in recommendations:
        print(rec)
    
    print("\n✅ Test complete!")
    
    # Save detailed results to file
    with open("rag_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_questions": total_questions,
                "successful_responses": successful_responses,
                "success_rate": successful_responses/total_questions if total_questions > 0 else 0,
                "average_latency": total_latency/successful_responses if successful_responses > 0 else 0
            },
            "results": all_results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: rag_test_results.json")

if __name__ == "__main__":
    # Check if server is running
    try:
        status = requests.get(f"{BASE_URL}/api/status")
        if status.status_code == 200:
            print("✅ Server is running. Starting tests...\n")
            run_comprehensive_test()
        else:
            print("❌ Server returned unexpected status:", status.status_code)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at", BASE_URL)
        print("Please ensure the FastAPI server is running: uvicorn app.main:app --reload")
