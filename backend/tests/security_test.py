#!/usr/bin/env python3
"""
Security Testing Script for Private GPT
Tests for common vulnerabilities and security issues
"""

import requests
import json
import time
from typing import Dict, List
import urllib3

# Disable SSL warnings for self-signed cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://44.202.131.48/api"

class SecurityTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
        self.session = requests.Session()
        self.session.verify = False  # For self-signed cert
        
    def test_injection_attacks(self):
        """Test for various injection vulnerabilities"""
        print("\n🔍 Testing Injection Attacks...")
        
        injection_payloads = [
            # SQL Injection attempts
            {"name": "SQL Injection", "payload": "'; DROP TABLE users; --"},
            {"name": "SQL Union", "payload": "' UNION SELECT * FROM users --"},
            
            # NoSQL Injection attempts
            {"name": "NoSQL Injection", "payload": '{"$ne": null}'},
            {"name": "NoSQL Regex", "payload": '{"$regex": ".*"}'},
            
            # Command Injection attempts
            {"name": "Command Injection", "payload": "; ls -la /etc/passwd"},
            {"name": "Command Chain", "payload": "test && cat /etc/passwd"},
            
            # Path Traversal attempts
            {"name": "Path Traversal", "payload": "../../../etc/passwd"},
            {"name": "URL Encoded Path", "payload": "..%2F..%2F..%2Fetc%2Fpasswd"},
            
            # Script Injection
            {"name": "Script Tag", "payload": "<script>alert('XSS')</script>"},
            {"name": "Event Handler", "payload": '<img src=x onerror="alert(1)">'},
            
            # Template Injection
            {"name": "Jinja2 Injection", "payload": "{{config.items()}}"},
            {"name": "Template Expression", "payload": "${7*7}"},
        ]
        
        for test in injection_payloads:
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/",
                    json={"message": test["payload"], "session_id": "security_test"},
                    timeout=10
                )
                
                # Check for suspicious responses
                suspicious = False
                if response.status_code != 200:
                    suspicious = True
                elif any(keyword in response.text.lower() for keyword in 
                        ['error', 'exception', 'traceback', 'syntax', 'passwd', 'config']):
                    suspicious = True
                
                self.results.append({
                    "test": test["name"],
                    "payload": test["payload"][:50],
                    "status": response.status_code,
                    "suspicious": suspicious,
                    "response_snippet": response.text[:100] if suspicious else "Normal"
                })
                
                print(f"  ✓ {test['name']}: {'⚠️ SUSPICIOUS' if suspicious else '✅ SAFE'}")
                
            except Exception as e:
                print(f"  ✗ {test['name']}: Error - {str(e)[:50]}")
    
    def test_rate_limiting(self):
        """Test if rate limiting is implemented"""
        print("\n🔍 Testing Rate Limiting...")
        
        rapid_requests = 20
        start_time = time.time()
        blocked_count = 0
        
        for i in range(rapid_requests):
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/",
                    json={"message": f"Test {i}", "session_id": "rate_test"},
                    timeout=5
                )
                
                if response.status_code == 429:  # Too Many Requests
                    blocked_count += 1
                elif response.status_code >= 500:
                    print(f"  ⚠️ Server error on request {i}: {response.status_code}")
                    
            except Exception as e:
                print(f"  ✗ Request {i} failed: {str(e)[:30]}")
        
        duration = time.time() - start_time
        
        if blocked_count > 0:
            print(f"  ✅ Rate limiting active: {blocked_count}/{rapid_requests} requests blocked")
        else:
            print(f"  ⚠️ No rate limiting detected! All {rapid_requests} requests in {duration:.1f}s succeeded")
    
    def test_authentication_bypass(self):
        """Test for authentication bypass vulnerabilities"""
        print("\n🔍 Testing Authentication Bypass...")
        
        bypass_attempts = [
            {"name": "Empty Session", "session_id": ""},
            {"name": "Null Session", "session_id": None},
            {"name": "Admin Session", "session_id": "admin"},
            {"name": "System Session", "session_id": "system"},
            {"name": "Special Chars", "session_id": "'; DROP TABLE sessions; --"},
            {"name": "Long Session", "session_id": "A" * 1000},
        ]
        
        for attempt in bypass_attempts:
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/",
                    json={"message": "Test message", "session_id": attempt["session_id"]},
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"  ⚠️ {attempt['name']}: Accepted (potential issue)")
                else:
                    print(f"  ✅ {attempt['name']}: Rejected ({response.status_code})")
                    
            except Exception as e:
                print(f"  ✓ {attempt['name']}: Rejected with error")
    
    def test_input_validation(self):
        """Test input validation and boundaries"""
        print("\n🔍 Testing Input Validation...")
        
        validation_tests = [
            {"name": "Empty Message", "message": "", "valid": False},
            {"name": "Whitespace Only", "message": "   \n\t  ", "valid": False},
            {"name": "Very Long Message", "message": "A" * 10000, "valid": False},
            {"name": "Unicode Characters", "message": "Test 你好 مرحبا 🚀", "valid": True},
            {"name": "Special Characters", "message": "!@#$%^&*()_+-=[]{}|;:,.<>?", "valid": True},
            {"name": "Null Bytes", "message": "Test\x00Message", "valid": False},
            {"name": "Control Characters", "message": "Test\x01\x02\x03Message", "valid": False},
        ]
        
        for test in validation_tests:
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/",
                    json={"message": test["message"], "session_id": "validation_test"},
                    timeout=10
                )
                
                success = response.status_code == 200
                expected = test["valid"]
                
                if success == expected:
                    print(f"  ✅ {test['name']}: Handled correctly")
                else:
                    print(f"  ⚠️ {test['name']}: Unexpected behavior")
                    
            except Exception as e:
                if not test["valid"]:
                    print(f"  ✅ {test['name']}: Properly rejected")
                else:
                    print(f"  ⚠️ {test['name']}: Should have been accepted")
    
    def test_dos_resistance(self):
        """Test resistance to denial of service attacks"""
        print("\n🔍 Testing DoS Resistance...")
        
        dos_tests = [
            {
                "name": "Large Payload",
                "payload": {"message": "A" * 100000, "session_id": "dos_test"}
            },
            {
                "name": "Deeply Nested JSON",
                "payload": {"message": "test", "session_id": "dos", 
                          "nested": {"level": 1, "data": {"level": 2, "data": {"level": 3}}}}
            },
            {
                "name": "Many Fields",
                "payload": {f"field_{i}": f"value_{i}" for i in range(1000)}
            },
        ]
        
        for test in dos_tests:
            try:
                start = time.time()
                response = self.session.post(
                    f"{self.base_url}/chat/",
                    json=test["payload"],
                    timeout=10
                )
                duration = time.time() - start
                
                if response.status_code in [400, 413, 422]:
                    print(f"  ✅ {test['name']}: Properly rejected")
                elif duration > 5:
                    print(f"  ⚠️ {test['name']}: Slow response ({duration:.1f}s)")
                else:
                    print(f"  ✓ {test['name']}: Handled ({duration:.1f}s)")
                    
            except requests.Timeout:
                print(f"  ⚠️ {test['name']}: Timeout (potential DoS)")
            except Exception as e:
                print(f"  ✅ {test['name']}: Rejected with error")
    
    def test_information_disclosure(self):
        """Test for information disclosure vulnerabilities"""
        print("\n🔍 Testing Information Disclosure...")
        
        # Test error messages
        try:
            response = self.session.get(f"{self.base_url}/nonexistent")
            if "fastapi" in response.text.lower() or "uvicorn" in response.text.lower():
                print("  ⚠️ Server technology disclosed in error pages")
            else:
                print("  ✅ Error pages don't reveal server details")
        except:
            print("  ✅ 404 handling appears secure")
        
        # Test headers
        try:
            response = self.session.get(f"{self.base_url}/health")
            headers_to_check = ['Server', 'X-Powered-By', 'X-AspNet-Version']
            disclosed = [h for h in headers_to_check if h in response.headers]
            
            if disclosed:
                print(f"  ⚠️ Sensitive headers exposed: {', '.join(disclosed)}")
            else:
                print("  ✅ No sensitive headers exposed")
                
        except:
            pass
        
        # Test debug mode
        try:
            response = self.session.post(
                f"{self.base_url}/chat/",
                json={"invalid_field": "test"},
                timeout=10
            )
            
            if "traceback" in response.text.lower() or "debug" in response.text.lower():
                print("  ⚠️ Debug information exposed in errors")
            else:
                print("  ✅ No debug information in error responses")
                
        except:
            print("  ✅ Error handling appears secure")
    
    def test_cors_configuration(self):
        """Test CORS configuration for security issues"""
        print("\n🔍 Testing CORS Configuration...")
        
        origins_to_test = [
            "https://evil.com",
            "null",
            "file://",
            "*"
        ]
        
        for origin in origins_to_test:
            try:
                response = self.session.options(
                    f"{self.base_url}/chat/",
                    headers={"Origin": origin}
                )
                
                allow_origin = response.headers.get("Access-Control-Allow-Origin")
                
                if allow_origin == origin or allow_origin == "*":
                    print(f"  ⚠️ Accepts origin: {origin}")
                else:
                    print(f"  ✅ Rejects origin: {origin}")
                    
            except:
                print(f"  ✓ Origin {origin} test completed")
    
    def generate_report(self):
        """Generate security test report"""
        print("\n" + "="*60)
        print("📋 SECURITY TEST SUMMARY")
        print("="*60)
        
        vulnerabilities = []
        warnings = []
        
        # Analyze results
        for result in self.results:
            if result.get("suspicious"):
                warnings.append(f"Potential issue with {result['test']}")
        
        if vulnerabilities:
            print("\n🚨 CRITICAL VULNERABILITIES:")
            for vuln in vulnerabilities:
                print(f"  • {vuln}")
        
        if warnings:
            print("\n⚠️ WARNINGS:")
            for warn in warnings:
                print(f"  • {warn}")
        
        if not vulnerabilities and not warnings:
            print("\n✅ No major security issues detected")
        
        print("\n📌 Recommendations:")
        print("  1. Implement rate limiting if not present")
        print("  2. Add input validation for all user inputs")
        print("  3. Use parameterized queries for any database operations")
        print("  4. Implement proper session management")
        print("  5. Regular security audits and penetration testing")
        print("  6. Keep all dependencies updated")

def main():
    """Run security tests"""
    print("\n" + "="*60)
    print("🔒 PRIVATE GPT SECURITY TESTING")
    print("="*60)
    
    tester = SecurityTester(API_URL)
    
    # Run all security tests
    tester.test_injection_attacks()
    tester.test_rate_limiting()
    tester.test_authentication_bypass()
    tester.test_input_validation()
    tester.test_dos_resistance()
    tester.test_information_disclosure()
    tester.test_cors_configuration()
    
    # Generate report
    tester.generate_report()

if __name__ == "__main__":
    main()
