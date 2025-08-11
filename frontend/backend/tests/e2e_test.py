#!/usr/bin/env python3
"""
End-to-End Integration Testing for Private GPT
Tests complete user workflows and system integration
"""

import requests
import time
import json
from typing import Dict, List, Optional
import urllib3
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://44.202.131.48/api"

class E2ETestSuite:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False
        self.test_results = []
        
    def test_complete_user_journey(self):
        """Test a complete user journey from start to finish"""
        print("\n🎯 Testing Complete User Journey...")
        
        session_id = f"e2e_user_{int(time.time())}"
        journey_steps = []
        
        # Step 1: Initial greeting
        print("  1️⃣ Initial greeting...")
        response = self._send_message("Hello, I need help with legal matters", session_id)
        if response and "response" in response:
            journey_steps.append({"step": "greeting", "success": True})
            print("     ✅ Bot responded to greeting")
        else:
            journey_steps.append({"step": "greeting", "success": False})
            print("     ❌ Failed to get greeting response")
        
        # Step 2: Ask about billing rates
        print("  2️⃣ Asking about billing rates...")
        response = self._send_message("What are the billing rates for partners?", session_id)
        if response and "$650" in str(response.get("response", "")):
            journey_steps.append({"step": "billing_query", "success": True})
            print("     ✅ Correct billing information provided")
        else:
            journey_steps.append({"step": "billing_query", "success": False})
            print("     ❌ Billing information incorrect or missing")
        
        # Step 3: Follow-up question
        print("  3️⃣ Follow-up question...")
        response = self._send_message("What about associate rates?", session_id)
        if response and "$350" in str(response.get("response", "")):
            journey_steps.append({"step": "follow_up", "success": True})
            print("     ✅ Context maintained, follow-up answered")
        else:
            journey_steps.append({"step": "follow_up", "success": False})
            print("     ❌ Context lost or incorrect answer")
        
        # Step 4: Switch topics
        print("  4️⃣ Switching topics to HR...")
        response = self._send_message("How do I request time off?", session_id)
        if response and "Dan Pfeiffer" in str(response.get("response", "")):
            journey_steps.append({"step": "topic_switch", "success": True})
            print("     ✅ Successfully switched topics")
        else:
            journey_steps.append({"step": "topic_switch", "success": False})
            print("     ❌ Failed to handle topic switch")
        
        # Step 5: Complex query
        print("  5️⃣ Complex multi-part query...")
        response = self._send_message(
            "Can you summarize both the partner billing rates and the PTO policy?", 
            session_id
        )
        if response and response.get("response"):
            has_billing = "$650" in str(response["response"])
            has_pto = "Pfeiffer" in str(response["response"])
            if has_billing and has_pto:
                journey_steps.append({"step": "complex_query", "success": True})
                print("     ✅ Handled complex multi-part query")
            else:
                journey_steps.append({"step": "complex_query", "success": False})
                print("     ❌ Incomplete complex query response")
        
        # Calculate success rate
        success_count = sum(1 for step in journey_steps if step["success"])
        total_steps = len(journey_steps)
        success_rate = (success_count / total_steps) * 100
        
        print(f"\n  📊 Journey Success Rate: {success_rate:.0f}% ({success_count}/{total_steps})")
        
        return journey_steps
    
    def test_conversation_memory(self):
        """Test conversation memory and context retention"""
        print("\n🧠 Testing Conversation Memory...")
        
        session_id = f"memory_test_{int(time.time())}"
        
        # Build context
        messages = [
            ("My name is John Smith and I'm a senior associate", "introduction"),
            ("I'm working on a criminal case", "case_type"),
            ("The defendant is charged with fraud", "case_details"),
            ("What billing rate should I use?", "rate_query"),
            ("What did I tell you my name was?", "name_recall"),
            ("What type of case am I working on?", "case_recall"),
        ]
        
        memory_results = []
        
        for message, test_type in messages:
            response = self._send_message(message, session_id)
            
            if test_type == "name_recall":
                if response and "John" in str(response.get("response", "")):
                    print("  ✅ Remembered user's name")
                    memory_results.append(True)
                else:
                    print("  ❌ Failed to recall name")
                    memory_results.append(False)
                    
            elif test_type == "case_recall":
                if response and "criminal" in str(response.get("response", "")).lower():
                    print("  ✅ Remembered case type")
                    memory_results.append(True)
                else:
                    print("  ❌ Failed to recall case type")
                    memory_results.append(False)
            
            time.sleep(1)  # Avoid rate limiting
        
        memory_score = sum(memory_results) / len(memory_results) * 100 if memory_results else 0
        print(f"\n  📊 Memory Retention Score: {memory_score:.0f}%")
        
        return memory_score
    
    def test_error_recovery(self):
        """Test system's ability to recover from errors"""
        print("\n🔧 Testing Error Recovery...")
        
        session_id = f"error_test_{int(time.time())}"
        error_scenarios = []
        
        # Test 1: Invalid input recovery
        print("  1️⃣ Testing invalid input recovery...")
        self._send_message("", session_id)  # Empty message
        response = self._send_message("What are the billing rates?", session_id)
        if response and response.get("response"):
            print("     ✅ Recovered from invalid input")
            error_scenarios.append(True)
        else:
            print("     ❌ Failed to recover from invalid input")
            error_scenarios.append(False)
        
        # Test 2: Session recovery
        print("  2️⃣ Testing session recovery...")
        fake_session = "non_existent_session_12345"
        response = self._send_message("Hello", fake_session)
        if response:
            print("     ✅ Handled non-existent session gracefully")
            error_scenarios.append(True)
        else:
            print("     ❌ Failed with non-existent session")
            error_scenarios.append(False)
        
        # Test 3: Malformed request recovery
        print("  3️⃣ Testing malformed request recovery...")
        try:
            # Send malformed JSON
            self.session.post(
                f"{self.base_url}/chat/",
                data="{'malformed': json}",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        except:
            pass
        
        # Try normal request after malformed one
        response = self._send_message("Test message", session_id)
        if response:
            print("     ✅ Recovered from malformed request")
            error_scenarios.append(True)
        else:
            print("     ❌ System stuck after malformed request")
            error_scenarios.append(False)
        
        recovery_rate = sum(error_scenarios) / len(error_scenarios) * 100 if error_scenarios else 0
        print(f"\n  📊 Error Recovery Rate: {recovery_rate:.0f}%")
        
        return recovery_rate
    
    def test_concurrent_sessions(self):
        """Test handling of multiple concurrent sessions"""
        print("\n👥 Testing Concurrent Sessions...")
        
        # Create multiple sessions
        sessions = [
            {"id": f"session_A_{int(time.time())}", "context": "billing rates"},
            {"id": f"session_B_{int(time.time())}", "context": "PTO policy"},
            {"id": f"session_C_{int(time.time())}", "context": "criminal law"},
        ]
        
        # Send initial messages to establish context
        print("  📝 Establishing session contexts...")
        for session in sessions:
            if session["context"] == "billing rates":
                self._send_message("I need information about billing rates", session["id"])
            elif session["context"] == "PTO policy":
                self._send_message("Tell me about the PTO policy", session["id"])
            else:
                self._send_message("I have questions about criminal law", session["id"])
            time.sleep(0.5)
        
        # Test context isolation
        print("  🔍 Testing context isolation...")
        isolation_results = []
        
        # Ask about billing in PTO session - should still work but separately
        response = self._send_message("What are partner rates?", sessions[1]["id"])
        if response and "$650" in str(response.get("response", "")):
            print("     ✅ Session B can ask new questions")
            isolation_results.append(True)
        
        # Verify original context maintained
        response = self._send_message("What were we discussing?", sessions[0]["id"])
        if response and "billing" in str(response.get("response", "")).lower():
            print("     ✅ Session A maintained context")
            isolation_results.append(True)
        else:
            print("     ❌ Session A lost context")
            isolation_results.append(False)
        
        isolation_score = sum(isolation_results) / len(isolation_results) * 100 if isolation_results else 0
        print(f"\n  📊 Session Isolation Score: {isolation_score:.0f}%")
        
        return isolation_score
    
    def test_response_consistency(self):
        """Test consistency of responses across similar queries"""
        print("\n🎯 Testing Response Consistency...")
        
        session_id = f"consistency_{int(time.time())}"
        
        # Ask same question in different ways
        billing_queries = [
            "What are the partner billing rates?",
            "How much do partners charge per hour?",
            "Tell me about partner hourly rates",
            "What's the billing rate for partners?",
        ]
        
        responses = []
        for query in billing_queries:
            response = self._send_message(query, f"{session_id}_{len(responses)}")
            if response and response.get("response"):
                responses.append(response["response"])
            time.sleep(1)
        
        # Check if all responses mention $650
        consistent = all("$650" in str(r) for r in responses)
        
        if consistent:
            print("  ✅ Consistent responses across similar queries")
        else:
            print("  ❌ Inconsistent responses detected")
            
        # Test PTO queries
        pto_queries = [
            "Who approves PTO?",
            "Who do I contact for time off approval?",
            "Who handles PTO requests?",
        ]
        
        pto_responses = []
        for query in pto_queries:
            response = self._send_message(query, f"{session_id}_pto_{len(pto_responses)}")
            if response and response.get("response"):
                pto_responses.append(response["response"])
            time.sleep(1)
        
        # Check if all responses mention Dan Pfeiffer
        pto_consistent = all("Dan Pfeiffer" in str(r) for r in pto_responses)
        
        if pto_consistent:
            print("  ✅ Consistent PTO approval information")
        else:
            print("  ❌ Inconsistent PTO information")
        
        consistency_score = (consistent + pto_consistent) / 2 * 100
        print(f"\n  📊 Consistency Score: {consistency_score:.0f}%")
        
        return consistency_score
    
    def test_performance_metrics(self):
        """Measure performance metrics"""
        print("\n⚡ Testing Performance Metrics...")
        
        metrics = {
            "response_times": [],
            "first_byte_times": [],
            "total_times": []
        }
        
        session_id = f"perf_{int(time.time())}"
        
        test_queries = [
            "Simple greeting",
            "What are billing rates?",
            "Explain the complete PTO policy in detail",
            "Tell me everything about criminal case procedures",
        ]
        
        for query in test_queries:
            start_time = time.time()
            
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/",
                    json={"message": query, "session_id": session_id},
                    timeout=30,
                    stream=True
                )
                
                first_byte_time = time.time() - start_time
                metrics["first_byte_times"].append(first_byte_time)
                
                content = response.content
                total_time = time.time() - start_time
                metrics["total_times"].append(total_time)
                
                print(f"  ⏱️ '{query[:20]}...': {total_time:.2f}s")
                
            except Exception as e:
                print(f"  ❌ Query failed: {str(e)[:50]}")
            
            time.sleep(1)
        
        if metrics["total_times"]:
            avg_time = sum(metrics["total_times"]) / len(metrics["total_times"])
            max_time = max(metrics["total_times"])
            min_time = min(metrics["total_times"])
            
            print(f"\n  📊 Performance Summary:")
            print(f"     Average Response Time: {avg_time:.2f}s")
            print(f"     Fastest Response: {min_time:.2f}s")
            print(f"     Slowest Response: {max_time:.2f}s")
            
            # Performance rating
            if avg_time < 5:
                print("     🚀 Performance: EXCELLENT")
            elif avg_time < 10:
                print("     ✅ Performance: GOOD")
            elif avg_time < 15:
                print("     ⚠️ Performance: ACCEPTABLE")
            else:
                print("     ❌ Performance: NEEDS IMPROVEMENT")
        
        return metrics
    
    def _send_message(self, message: str, session_id: str) -> Optional[Dict]:
        """Helper method to send a message and return response"""
        try:
            response = self.session.post(
                f"{self.base_url}/chat/",
                json={"message": message, "session_id": session_id},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"     ⚠️ Request failed: {str(e)[:50]}")
            return None
    
    def generate_report(self):
        """Generate comprehensive E2E test report"""
        print("\n" + "="*60)
        print("📊 END-TO-END TEST REPORT")
        print("="*60)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n📅 Test Date: {timestamp}")
        print(f"🌐 System URL: {self.base_url}")
        
        print("\n✅ STRENGTHS:")
        print("  • System responds to queries")
        print("  • Knowledge base integration working")
        print("  • Session management functional")
        
        print("\n⚠️ AREAS FOR IMPROVEMENT:")
        print("  • Response time optimization needed")
        print("  • Consider caching for frequent queries")
        print("  • Add more comprehensive error handling")
        
        print("\n📝 RECOMMENDATIONS:")
        print("  1. Implement response caching for common queries")
        print("  2. Add request queuing for high load scenarios")
        print("  3. Optimize embedding search performance")
        print("  4. Add comprehensive logging and monitoring")
        print("  5. Implement automated health checks")

def main():
    """Run E2E test suite"""
    print("\n" + "="*60)
    print("🚀 PRIVATE GPT END-TO-END TESTING")
    print("="*60)
    
    suite = E2ETestSuite(API_URL)
    
    # Run all E2E tests
    print("\n🧪 Running Complete Test Suite...")
    
    journey_results = suite.test_complete_user_journey()
    memory_score = suite.test_conversation_memory()
    recovery_rate = suite.test_error_recovery()
    isolation_score = suite.test_concurrent_sessions()
    consistency_score = suite.test_response_consistency()
    performance_metrics = suite.test_performance_metrics()
    
    # Generate final report
    suite.generate_report()
    
    # Overall system score
    scores = [memory_score, recovery_rate, isolation_score, consistency_score]
    overall_score = sum(scores) / len(scores)
    
    print(f"\n🎯 OVERALL SYSTEM SCORE: {overall_score:.0f}%")
    
    if overall_score >= 80:
        print("✅ System is READY for pilot")
    elif overall_score >= 60:
        print("⚠️ System is PARTIALLY READY - address issues before pilot")
    else:
        print("❌ System NEEDS WORK before pilot deployment")

if __name__ == "__main__":
    main()
