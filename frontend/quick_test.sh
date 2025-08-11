#!/bin/bash

# Quick Validation Test - Run this to verify system is working

echo "================================"
echo "Quick System Validation Test"
echo "================================"
echo ""

API_URL="https://44.202.131.48/api"
PASSED=0
FAILED=0

# Test 1: System Health
echo -n "1. System Health Check... "
if curl -s "$API_URL/health" -k 2>/dev/null | grep -q "healthy"; then
    echo "✅ PASS"
    PASSED=$((PASSED + 1))
else
    echo "❌ FAIL"
    FAILED=$((FAILED + 1))
fi

# Test 2: Knowledge Base Query
echo -n "2. Knowledge Base Test... "
response=$(curl -s -X POST "$API_URL/chat/" \
    -H "Content-Type: application/json" \
    -k \
    -d '{"message":"What are partner billing rates?"}' 2>/dev/null)

if echo "$response" | grep -q "850\|650"; then
    echo "✅ PASS (Found billing rates)"
    PASSED=$((PASSED + 1))
else
    echo "❌ FAIL (No billing rates found)"
    FAILED=$((FAILED + 1))
fi

# Test 3: Response Time
echo -n "3. Response Time Test... "
start=$(date +%s)
curl -s -X POST "$API_URL/chat/" \
    -H "Content-Type: application/json" \
    -k \
    -d '{"message":"What is the PTO policy?"}' > /dev/null 2>&1
end=$(date +%s)
elapsed=$((end - start))

if [ $elapsed -lt 10 ]; then
    echo "✅ PASS (${elapsed}s)"
    PASSED=$((PASSED + 1))
else
    echo "⚠️  SLOW (${elapsed}s)"
    FAILED=$((FAILED + 1))
fi

# Test 4: Context Maintenance
echo -n "4. Conversation Context Test... "
SESSION="quick-test-$$"

# First message
curl -s -X POST "$API_URL/chat/" \
    -H "Content-Type: application/json" \
    -H "User-Agent: $SESSION" \
    -k \
    -d '{"message":"What types of cases do you handle?"}' > /dev/null 2>&1

# Follow-up
response=$(curl -s -X POST "$API_URL/chat/" \
    -H "Content-Type: application/json" \
    -H "User-Agent: $SESSION" \
    -k \
    -d '{"message":"Tell me more about criminal cases"}' 2>/dev/null)

if echo "$response" | grep -qi "criminal\|white collar\|federal"; then
    echo "✅ PASS (Context maintained)"
    PASSED=$((PASSED + 1))
else
    echo "❌ FAIL (Context lost)"
    FAILED=$((FAILED + 1))
fi

# Test 5: Frontend Access
echo -n "5. Frontend Web Access... "
if curl -s -k -I "https://44.202.131.48" 2>/dev/null | grep -q "200\|304"; then
    echo "✅ PASS"
    PASSED=$((PASSED + 1))
else
    echo "❌ FAIL"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "================================"
echo "Results: $PASSED passed, $FAILED failed"

if [ $FAILED -eq 0 ]; then
    echo "✅ SYSTEM READY FOR TESTING"
else
    echo "⚠️  ISSUES DETECTED - Review failures"
fi

echo "================================"
echo ""
echo "Access the system at: https://44.202.131.48"
