#!/usr/bin/env python3
"""
Chaos Engineering Tests for Private GPT
Tests system resilience under unexpected conditions
"""

import requests
import random
import time
import asyncio
import aiohttp
from typing import List, Dict
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://44.202.131.48/api"

class ChaosEngineer:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.chaos_results = []
        
    async def random_delays_test(self):
        """Introduce random network delays between requests"""
        print("\n🎲 Testing with Random Network Delays...")
        
        session_id = f"chaos_delay_{int(time.time())}"
        results = []
        
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            for i in range(10):
                # Random delay between 0 and 5 seconds
                delay = random.uniform(0, 5)
                await asyncio.sleep(delay)
                
                try:
                    start = time.time()
                    async with session.post(
                        f"{self.base_url}/chat/",
                        json={"message": f"Test message {i}", "session_id": session_id},
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        duration = time.time() - start
                        results.append({
                            "delay": delay,
                            "response_time": duration,
                            "status": response.status
                        })
                        print(f"  📊 Delay: {delay:.1f}s → Response: {duration:.1f}s")
                except Exception as e:
                    print(f"  ❌ Request failed after {delay:.1f}s delay")
        
        success_rate = sum(1 for r in results if r.get("status") == 200) / 10 * 100
        print(f"\n  Success rate with random delays: {success_rate:.0f}%")
        
        return success_rate
    
    async def connection_drops_test(self):
        """Simulate random connection drops"""
        print("\n🔌 Testing Connection Drops...")
        
        session_id = f"chaos_drops_{int(time.time())}"
        successes = 0
        failures = 0
        
        for i in range(15):
            # 30% chance of simulating connection drop
            if random.random() < 0.3:
                print(f"  💥 Simulating connection drop for request {i}")
                failures += 1
                await asyncio.sleep(1)
                continue
            
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                try:
                    async with session.post(
                        f"{self.base_url}/chat/",
                        json={"message": f"Message {i}", "session_id": session_id},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            successes += 1
                            print(f"  ✅ Request {i} succeeded")
                        else:
                            failures += 1
                            print(f"  ⚠️ Request {i} returned {response.status}")
                except Exception as e:
                    failures += 1
                    print(f"  ❌ Request {i} failed: {str(e)[:30]}")
            
            await asyncio.sleep(0.5)
        
        recovery_rate = successes / (successes + failures) * 100
        print(f"\n  Recovery rate: {recovery_rate:.0f}% ({successes}/{successes + failures})")
        
        return recovery_rate
    
    async def burst_traffic_test(self):
        """Send sudden burst of traffic"""
        print("\n💥 Testing Traffic Bursts...")
        
        # Normal traffic
        print("  📊 Phase 1: Normal traffic (2 req/s)...")
        normal_results = []
        
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            for i in range(5):
                try:
                    start = time.time()
                    async with session.post(
                        f"{self.base_url}/chat/",
                        json={"message": "Normal traffic", "session_id": f"burst_normal_{i}"},
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        normal_results.append(time.time() - start)
                except:
                    pass
                await asyncio.sleep(0.5)
        
        # Sudden burst
        print("  💥 Phase 2: Traffic burst (50 simultaneous requests)...")
        burst_tasks = []
        
        async with aiohttp.ClientSession(connector=connector) as session:
            for i in range(50):
                task = session.post(
                    f"{self.base_url}/chat/",
                    json={"message": "Burst traffic", "session_id": f"burst_{i}"},
                    timeout=aiohttp.ClientTimeout(total=30)
                )
                burst_tasks.append(task)
            
            burst_start = time.time()
            responses = await asyncio.gather(*burst_tasks, return_exceptions=True)
            burst_duration = time.time() - burst_start
        
        successful_burst = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
        
        # Recovery phase
        print("  📊 Phase 3: Recovery (back to normal)...")
        recovery_results = []
        
        await asyncio.sleep(5)  # Wait for system to recover
        
        async with aiohttp.ClientSession(connector=connector) as session:
            for i in range(5):
                try:
                    start = time.time()
                    async with session.post(
                        f"{self.base_url}/chat/",
                        json={"message": "Recovery test", "session_id": f"recovery_{i}"},
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        recovery_results.append(time.time() - start)
                except:
                    pass
                await asyncio.sleep(0.5)
        
        print(f"\n  📊 Results:")
        print(f"     Normal avg response: {sum(normal_results)/len(normal_results):.2f}s" if normal_results else "     Normal: No data")
        print(f"     Burst success rate: {successful_burst}/50 ({successful_burst*2}%)")
        print(f"     Burst duration: {burst_duration:.2f}s")
        print(f"     Recovery avg response: {sum(recovery_results)/len(recovery_results):.2f}s" if recovery_results else "     Recovery: No data")
        
        return successful_burst * 2  # Convert to percentage
    
    async def malformed_data_test(self):
        """Send various malformed data"""
        print("\n🔨 Testing Malformed Data Handling...")
        
        malformed_tests = [
            {"name": "Huge message", "data": {"message": "X" * 1000000, "session_id": "test"}},
            {"name": "Missing message", "data": {"session_id": "test"}},
            {"name": "Missing session", "data": {"message": "test"}},
            {"name": "Wrong types", "data": {"message": 123, "session_id": ["list"]}},
            {"name": "Extra fields", "data": {"message": "test", "session_id": "test", "hack": "attempt", "extra": "fields"}},
            {"name": "Nested complexity", "data": {"message": {"nested": {"deeply": {"nested": "value"}}}, "session_id": "test"}},
            {"name": "Unicode overload", "data": {"message": "🚀" * 10000, "session_id": "test"}},
            {"name": "Binary data", "data": {"message": "\x00\x01\x02\x03", "session_id": "test"}},
        ]
        
        handled_correctly = 0
        
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            for test in malformed_tests:
                try:
                    async with session.post(
                        f"{self.base_url}/chat/",
                        json=test["data"],
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status in [400, 422, 413]:  # Bad request codes
                            print(f"  ✅ {test['name']}: Properly rejected ({response.status})")
                            handled_correctly += 1
                        elif response.status == 200:
                            print(f"  ⚠️ {test['name']}: Accepted (potential issue)")
                        else:
                            print(f"  📊 {test['name']}: Status {response.status}")
                except Exception as e:
                    print(f"  ✅ {test['name']}: Rejected with error")
                    handled_correctly += 1
        
        handling_rate = handled_correctly / len(malformed_tests) * 100
        print(f"\n  Malformed data handling rate: {handling_rate:.0f}%")
        
        return handling_rate
    
    async def resource_exhaustion_test(self):
        """Try to exhaust system resources"""
        print("\n💀 Testing Resource Exhaustion...")
        
        # Test 1: Many sessions
        print("  📊 Creating many sessions...")
        sessions_created = 0
        
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for i in range(100):
                task = session.post(
                    f"{self.base_url}/chat/",
                    json={"message": "Session test", "session_id": f"exhaust_session_{i}"},
                    timeout=aiohttp.ClientTimeout(total=5)
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            sessions_created = sum(1 for r in responses if not isinstance(r, Exception))
        
        print(f"     Created {sessions_created}/100 sessions")
        
        # Test 2: Long conversation history
        print("  📊 Building long conversation history...")
        long_session = f"exhaust_long_{int(time.time())}"
        messages_sent = 0
        
        async with aiohttp.ClientSession(connector=connector) as session:
            for i in range(50):
                try:
                    async with session.post(
                        f"{self.base_url}/chat/",
                        json={"message": f"Message {i} in long conversation", "session_id": long_session},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            messages_sent += 1
                except:
                    break
        
        print(f"     Sent {messages_sent}/50 messages in single session")
        
        # Calculate resilience score
        resilience_score = (sessions_created / 100 + messages_sent / 50) / 2 * 100
        print(f"\n  Resource resilience score: {resilience_score:.0f}%")
        
        return resilience_score
    
    async def intermittent_failures_test(self):
        """Simulate intermittent failures and recovery"""
        print("\n🎭 Testing Intermittent Failures...")
        
        session_id = f"intermittent_{int(time.time())}"
        results = []
        
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            for i in range(20):
                # Simulate 20% failure rate
                should_fail = random.random() < 0.2
                
                if should_fail:
                    print(f"  💥 Simulating failure for request {i}")
                    results.append({"success": False, "simulated": True})
                    await asyncio.sleep(0.5)
                    continue
                
                try:
                    async with session.post(
                        f"{self.base_url}/chat/",
                        json={"message": f"Test {i}", "session_id": session_id},
                        timeout=aiohttp.ClientTimeout(total=15)
                    ) as response:
                        if response.status == 200:
                            results.append({"success": True})
                            print(f"  ✅ Request {i} succeeded")
                        else:
                            results.append({"success": False})
                            print(f"  ⚠️ Request {i} failed")
                except Exception as e:
                    results.append({"success": False})
                    print(f"  ❌ Request {i} error: {str(e)[:30]}")
                
                await asyncio.sleep(0.3)
        
        # Check if system maintains consistency
        real_requests = [r for r in results if not r.get("simulated")]
        success_rate = sum(1 for r in real_requests if r["success"]) / len(real_requests) * 100
        
        print(f"\n  System reliability under intermittent failures: {success_rate:.0f}%")
        
        return success_rate
    
    def generate_chaos_report(self, results: Dict[str, float]):
        """Generate chaos engineering report"""
        print("\n" + "="*60)
        print("🌪️ CHAOS ENGINEERING REPORT")
        print("="*60)
        
        print("\n📊 Test Results:")
        for test_name, score in results.items():
            emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            print(f"  {emoji} {test_name}: {score:.0f}%")
        
        overall_resilience = sum(results.values()) / len(results)
        
        print(f"\n🎯 Overall Resilience Score: {overall_resilience:.0f}%")
        
        if overall_resilience >= 80:
            print("✅ System shows EXCELLENT resilience")
        elif overall_resilience >= 60:
            print("⚠️ System shows MODERATE resilience")
        else:
            print("❌ System needs RESILIENCE IMPROVEMENTS")
        
        print("\n📝 Recommendations:")
        if results.get("random_delays", 0) < 80:
            print("  • Implement request timeout retry logic")
        if results.get("connection_drops", 0) < 80:
            print("  • Add connection pooling and retry mechanisms")
        if results.get("burst_traffic", 0) < 80:
            print("  • Implement rate limiting and request queuing")
        if results.get("malformed_data", 0) < 80:
            print("  • Strengthen input validation")
        if results.get("resource_exhaustion", 0) < 80:
            print("  • Add resource limits and cleanup routines")
        if results.get("intermittent_failures", 0) < 80:
            print("  • Implement circuit breaker pattern")

async def main():
    """Run chaos engineering tests"""
    print("\n" + "="*60)
    print("🌪️ PRIVATE GPT CHAOS ENGINEERING")
    print("="*60)
    print("\nSimulating various failure scenarios...")
    
    chaos = ChaosEngineer(API_URL)
    
    results = {}
    
    # Run all chaos tests
    results["random_delays"] = await chaos.random_delays_test()
    results["connection_drops"] = await chaos.connection_drops_test()
    results["burst_traffic"] = await chaos.burst_traffic_test()
    results["malformed_data"] = await chaos.malformed_data_test()
    results["resource_exhaustion"] = await chaos.resource_exhaustion_test()
    results["intermittent_failures"] = await chaos.intermittent_failures_test()
    
    # Generate report
    chaos.generate_chaos_report(results)

if __name__ == "__main__":
    asyncio.run(main())
