#!/usr/bin/env python3
"""
Load Testing Script for Private GPT
Tests system performance under concurrent user load
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict
import json
from datetime import datetime

API_URL = "https://44.202.131.48/api"

# Test scenarios
TEST_QUERIES = [
    "What are the billing rates for partners?",
    "How do I request PTO?",
    "What's the remote work policy?",
    "Tell me about criminal case procedures",
    "What are associate billing rates?",
    "Who approves time off requests?",
    "Explain the jurisdiction for federal cases",
    "What's the policy on working from home?",
    "How are legal fees structured?",
    "What are the firm's HR policies?"
]

class LoadTester:
    def __init__(self, base_url: str, verify_ssl: bool = False):
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        self.results = []
        
    async def single_user_session(self, user_id: int, num_queries: int = 5):
        """Simulate a single user session with multiple queries"""
        session_id = f"user_{user_id}_{int(time.time())}"
        session_results = []
        
        connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
        async with aiohttp.ClientSession(connector=connector) as session:
            for i in range(num_queries):
                query = TEST_QUERIES[i % len(TEST_QUERIES)]
                start_time = time.time()
                
                try:
                    async with session.post(
                        f"{self.base_url}/chat/",
                        json={"message": query, "session_id": session_id},
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        result = await response.json()
                        end_time = time.time()
                        
                        session_results.append({
                            "user_id": user_id,
                            "query_num": i + 1,
                            "response_time": end_time - start_time,
                            "status": response.status,
                            "success": response.status == 200,
                            "query": query[:50] + "..."
                        })
                except Exception as e:
                    end_time = time.time()
                    session_results.append({
                        "user_id": user_id,
                        "query_num": i + 1,
                        "response_time": end_time - start_time,
                        "status": 0,
                        "success": False,
                        "error": str(e),
                        "query": query[:50] + "..."
                    })
                
                # Small delay between queries to simulate real user
                await asyncio.sleep(0.5)
        
        return session_results
    
    async def run_concurrent_users(self, num_users: int, queries_per_user: int = 3):
        """Run multiple concurrent user sessions"""
        print(f"\n🚀 Starting load test with {num_users} concurrent users...")
        print(f"   Each user will make {queries_per_user} queries")
        
        start_time = time.time()
        
        # Create tasks for all users
        tasks = [
            self.single_user_session(user_id, queries_per_user)
            for user_id in range(num_users)
        ]
        
        # Run all user sessions concurrently
        all_results = await asyncio.gather(*tasks)
        
        # Flatten results
        for user_results in all_results:
            self.results.extend(user_results)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        self.print_statistics(num_users, total_time)
    
    def print_statistics(self, num_users: int, total_time: float):
        """Print load test statistics"""
        successful = [r for r in self.results if r.get("success", False)]
        failed = [r for r in self.results if not r.get("success", False)]
        response_times = [r["response_time"] for r in successful]
        
        print("\n" + "="*60)
        print("📊 LOAD TEST RESULTS")
        print("="*60)
        
        print(f"\n⏱️  Total test duration: {total_time:.2f} seconds")
        print(f"👥 Concurrent users: {num_users}")
        print(f"📨 Total requests: {len(self.results)}")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        
        if successful:
            print(f"\n📈 Response Time Statistics (successful requests):")
            print(f"   Min: {min(response_times):.2f}s")
            print(f"   Max: {max(response_times):.2f}s")
            print(f"   Mean: {statistics.mean(response_times):.2f}s")
            print(f"   Median: {statistics.median(response_times):.2f}s")
            if len(response_times) > 1:
                print(f"   Std Dev: {statistics.stdev(response_times):.2f}s")
            
            # Calculate percentiles
            sorted_times = sorted(response_times)
            p50 = sorted_times[len(sorted_times)//2]
            p90 = sorted_times[int(len(sorted_times)*0.9)]
            p95 = sorted_times[int(len(sorted_times)*0.95)]
            print(f"\n📊 Percentiles:")
            print(f"   50th (median): {p50:.2f}s")
            print(f"   90th: {p90:.2f}s")
            print(f"   95th: {p95:.2f}s")
        
        if failed:
            print(f"\n⚠️  Failed Requests Analysis:")
            errors = {}
            for r in failed:
                error = r.get("error", "Unknown error")
                errors[error] = errors.get(error, 0) + 1
            for error, count in errors.items():
                print(f"   {error[:50]}: {count} occurrences")
        
        # Throughput
        throughput = len(self.results) / total_time
        print(f"\n🚀 Throughput: {throughput:.2f} requests/second")
        
        # Save detailed results
        self.save_results()
    
    def save_results(self):
        """Save detailed results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {filename}")

async def progressive_load_test():
    """Run progressive load tests with increasing users"""
    tester = LoadTester(API_URL)
    
    print("\n" + "="*60)
    print("🔄 PROGRESSIVE LOAD TEST")
    print("="*60)
    
    user_counts = [1, 3, 5, 10]
    
    for num_users in user_counts:
        print(f"\n📍 Testing with {num_users} concurrent users...")
        tester.results = []  # Reset results
        await tester.run_concurrent_users(num_users, queries_per_user=2)
        
        # Wait between tests
        if num_users < user_counts[-1]:
            print(f"\n⏳ Waiting 10 seconds before next test...")
            await asyncio.sleep(10)

async def spike_test():
    """Simulate sudden spike in traffic"""
    tester = LoadTester(API_URL)
    
    print("\n" + "="*60)
    print("⚡ SPIKE TEST")
    print("="*60)
    print("Simulating sudden traffic spike...")
    
    # Start with normal load
    print("\n📍 Phase 1: Normal load (2 users)")
    await tester.run_concurrent_users(2, queries_per_user=2)
    
    # Sudden spike
    print("\n📍 Phase 2: Traffic spike (15 users)")
    tester.results = []
    await tester.run_concurrent_users(15, queries_per_user=1)
    
    # Return to normal
    print("\n📍 Phase 3: Return to normal (2 users)")
    tester.results = []
    await tester.run_concurrent_users(2, queries_per_user=2)

async def endurance_test():
    """Run sustained load for extended period"""
    tester = LoadTester(API_URL)
    
    print("\n" + "="*60)
    print("⏰ ENDURANCE TEST")
    print("="*60)
    print("Running sustained load for 5 minutes...")
    
    start_time = time.time()
    test_duration = 300  # 5 minutes
    iteration = 0
    
    while (time.time() - start_time) < test_duration:
        iteration += 1
        print(f"\n🔄 Iteration {iteration}")
        tester.results = []
        await tester.run_concurrent_users(3, queries_per_user=3)
        
        elapsed = time.time() - start_time
        remaining = test_duration - elapsed
        if remaining > 0:
            print(f"⏳ {remaining:.0f} seconds remaining...")
            await asyncio.sleep(min(10, remaining))
    
    print("\n✅ Endurance test completed!")

def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("🧪 PRIVATE GPT LOAD TESTING SUITE")
    print("="*60)
    
    print("\nSelect test type:")
    print("1. Quick Load Test (5 concurrent users)")
    print("2. Progressive Load Test (1 → 10 users)")
    print("3. Spike Test (sudden traffic increase)")
    print("4. Endurance Test (5 minutes sustained load)")
    print("5. Custom Load Test")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        asyncio.run(LoadTester(API_URL).run_concurrent_users(5, 3))
    elif choice == "2":
        asyncio.run(progressive_load_test())
    elif choice == "3":
        asyncio.run(spike_test())
    elif choice == "4":
        asyncio.run(endurance_test())
    elif choice == "5":
        users = int(input("Number of concurrent users: "))
        queries = int(input("Queries per user: "))
        asyncio.run(LoadTester(API_URL).run_concurrent_users(users, queries))
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
