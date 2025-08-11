#!/bin/bash

# Comprehensive Test Suite for Private GPT
# Run this to validate all system functionality

set -e

API_URL="https://44.202.131.48/api"
RESULTS_FILE="test_results_$(date +%Y%m%d_%H%M%S).txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================" | tee $RESULTS_FILE
echo "Private GPT Comprehensive Test Suite" | tee -a $RESULTS_FILE
echo "Started: $(date)" | tee -a $RESULTS_FILE
echo "=========================================" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

PASSED=0
FAILED=0

# Function to test API endpoint
test_query() {
    local test_name="$1"
    local query="$2"
    local expected="$3"
    local description="$4"
    
    echo -n "Testing: $test_name... " | tee -a $RESULTS_FILE
    
    # Make the API call
    response=$(curl -s -X POST "$API_URL/chat/" \
        -H "Content-Type: application/json" \
        -H "User-Agent: TestSuite-$$" \
        -k \
        -d "{\"message\":\"$query\"}" 2>/dev/null)
    
    # Check if response contains expected content
    if echo "$response" | grep -qi "$expected"; then
        echo -e "${GREEN}✅ PASS${NC}" | tee -a $RESULTS_FILE
        echo "  Expected: Found '$expected'" | tee -a $RESULTS_FILE
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}" | tee -a $RESULTS_FILE
        echo "  Expected: '$expected' but got:" | tee -a $RESULTS_FILE
        echo "$response" | python3 -c "import sys, json; print('  Response:', json.load(sys.stdin).get('content', 'No content')[:200])" 2>/dev/null | tee -a $RESULTS_FILE
        FAILED=$((FAILED + 1))
    fi
    echo "" | tee -a $RESULTS_FILE
    
    sleep 1  # Rate limiting
}

# Function to test conversation continuity
test_conversation() {
    local test_name="$1"
    local query1="$2"
    local query2="$3"
    local expected="$4"
    
    echo "Testing Conversation: $test_name" | tee -a $RESULTS_FILE
    
    # Generate unique session ID for this test
    SESSION_ID="test-conv-$$-$(date +%s)"
    
    # First query
    echo -n "  Q1: $query1... " | tee -a $RESULTS_FILE
    response1=$(curl -s -X POST "$API_URL/chat/" \
        -H "Content-Type: application/json" \
        -H "User-Agent: $SESSION_ID" \
        -k \
        -d "{\"message\":\"$query1\"}" 2>/dev/null)
    echo -e "${GREEN}sent${NC}" | tee -a $RESULTS_FILE
    
    sleep 1
    
    # Follow-up query
    echo -n "  Q2: $query2... " | tee -a $RESULTS_FILE
    response2=$(curl -s -X POST "$API_URL/chat/" \
        -H "Content-Type: application/json" \
        -H "User-Agent: $SESSION_ID" \
        -k \
        -d "{\"message\":\"$query2\"}" 2>/dev/null)
    
    if echo "$response2" | grep -qi "$expected"; then
        echo -e "${GREEN}✅ Context maintained${NC}" | tee -a $RESULTS_FILE
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ Context lost${NC}" | tee -a $RESULTS_FILE
        FAILED=$((FAILED + 1))
    fi
    echo "" | tee -a $RESULTS_FILE
    
    sleep 1
}

# Function to test response time
test_performance() {
    local query="$1"
    
    echo -n "Performance Test: " | tee -a $RESULTS_FILE
    
    start_time=$(date +%s%N)
    curl -s -X POST "$API_URL/chat/" \
        -H "Content-Type: application/json" \
        -k \
        -d "{\"message\":\"$query\"}" > /dev/null 2>&1
    end_time=$(date +%s%N)
    
    elapsed=$((($end_time - $start_time) / 1000000))
    
    if [ $elapsed -lt 10000 ]; then
        echo -e "${GREEN}✅ Response time: ${elapsed}ms${NC}" | tee -a $RESULTS_FILE
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⚠️  Slow response: ${elapsed}ms${NC}" | tee -a $RESULTS_FILE
        FAILED=$((FAILED + 1))
    fi
    echo "" | tee -a $RESULTS_FILE
}

echo "===== SECTION 1: INFRASTRUCTURE TESTS =====" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

# Test 1: Health Check
echo -n "1. Health Check Endpoint... " | tee -a $RESULTS_FILE
if curl -s "$API_URL/health" -k | grep -q "healthy"; then
    echo -e "${GREEN}✅ PASS${NC}" | tee -a $RESULTS_FILE
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC}" | tee -a $RESULTS_FILE
    FAILED=$((FAILED + 1))
fi

# Test 2: Frontend Accessibility
echo -n "2. Frontend HTTPS Access... " | tee -a $RESULTS_FILE
if curl -s -k -I "https://44.202.131.48" | grep -q "200\|304"; then
    echo -e "${GREEN}✅ PASS${NC}" | tee -a $RESULTS_FILE
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC}" | tee -a $RESULTS_FILE
    FAILED=$((FAILED + 1))
fi

echo "" | tee -a $RESULTS_FILE
echo "===== SECTION 2: KNOWLEDGE BASE TESTS =====" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

# HR Policy Tests
test_query "3. Remote Work Policy" \
    "What is the remote work policy?" \
    "supervisor" \
    "Should mention supervisor approval"

test_query "4. Remote Work Equipment" \
    "What equipment does the firm provide for remote work?" \
    "laptop" \
    "Should mention laptop, VPN, etc."

test_query "5. PTO Accrual Rates" \
    "How much PTO do employees get?" \
    "15 days" \
    "Should mention 15 days for years 1-3"

test_query "6. Sick Leave Policy" \
    "What is the sick leave policy?" \
    "10 days" \
    "Should mention 10 days per year"

test_query "7. Parental Leave" \
    "What is the parental leave policy?" \
    "12 weeks" \
    "Should mention 12 weeks paid leave"

echo "===== SECTION 3: BILLING & RATES TESTS =====" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

test_query "8. Partner Billing Rates" \
    "What are the billing rates for partners?" \
    "850" \
    "Should include partner rates"

test_query "9. Associate Rates" \
    "What do associates charge per hour?" \
    "295\|350\|450" \
    "Should mention associate rate ranges"

test_query "10. Paralegal Rates" \
    "What are paralegal billing rates?" \
    "195\|225" \
    "Should mention paralegal rates"

test_query "11. Retainer Amount" \
    "What is the standard retainer amount?" \
    "10,000\|10000" \
    "Should mention $10,000 retainer"

test_query "12. Billing Increment" \
    "What is the minimum billing increment?" \
    "6 minute\|0.1 hour" \
    "Should mention 6-minute or 0.1 hour"

echo "===== SECTION 4: LEGAL PRACTICE TESTS =====" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

test_query "13. Criminal Case Types" \
    "What types of criminal cases do you handle?" \
    "white collar" \
    "Should mention white collar crimes"

test_query "14. Federal Criminal Defense" \
    "Do you handle federal criminal cases?" \
    "federal" \
    "Should confirm federal criminal defense"

test_query "15. Litigation Hold" \
    "What is a litigation hold?" \
    "preserve\|preservation" \
    "Should mention document preservation"

test_query "16. Discovery Process" \
    "What is included in the discovery phase?" \
    "deposition\|interrogator" \
    "Should mention depositions or interrogatories"

test_query "17. Civil Litigation Steps" \
    "What are the steps in civil litigation?" \
    "complaint\|discovery\|trial" \
    "Should outline litigation process"

echo "===== SECTION 5: CONVERSATION CONTEXT TESTS =====" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

test_conversation "18. Context Test - Case Types" \
    "What types of cases do you handle?" \
    "Tell me more about the criminal cases" \
    "criminal\|white collar\|federal"

test_conversation "19. Context Test - Billing" \
    "What are your billing rates?" \
    "What about for new clients?" \
    "rate\|hour\|retainer"

test_conversation "20. Context Test - PTO" \
    "How much vacation time do employees get?" \
    "What about after 5 years?" \
    "20 days\|years 4-6"

echo "===== SECTION 6: EDGE CASE TESTS =====" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

test_query "21. Nonsense Query" \
    "asdkfjaslkdfj aslkdfj alskdfj" \
    "don't have\|unable\|understand" \
    "Should handle gracefully"

test_query "22. Off-topic Query" \
    "What's the weather like?" \
    "don't have\|unable\|not available" \
    "Should indicate info not available"

test_query "23. Empty-like Query" \
    "???" \
    "help\|assist\|clarify" \
    "Should ask for clarification"

echo "===== SECTION 7: PERFORMANCE TESTS =====" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

test_performance "What are the billing rates?"
test_performance "Tell me about remote work policy"
test_performance "What types of cases do you handle?"

echo "===== SECTION 8: STRESS TESTS =====" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

echo -n "24. Rapid Sequential Queries... " | tee -a $RESULTS_FILE
success=0
for i in {1..5}; do
    response=$(curl -s -X POST "$API_URL/chat/" \
        -H "Content-Type: application/json" \
        -H "User-Agent: StressTest-$i" \
        -k \
        -d '{"message":"What is the PTO policy?"}' 2>/dev/null)
    if echo "$response" | grep -q "content"; then
        success=$((success + 1))
    fi
done

if [ $success -eq 5 ]; then
    echo -e "${GREEN}✅ All 5 requests succeeded${NC}" | tee -a $RESULTS_FILE
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️  $success/5 requests succeeded${NC}" | tee -a $RESULTS_FILE
    FAILED=$((FAILED + 1))
fi

echo "" | tee -a $RESULTS_FILE
echo "=========================================" | tee -a $RESULTS_FILE
echo "TEST RESULTS SUMMARY" | tee -a $RESULTS_FILE
echo "=========================================" | tee -a $RESULTS_FILE
echo -e "Passed: ${GREEN}$PASSED${NC}" | tee -a $RESULTS_FILE
echo -e "Failed: ${RED}$FAILED${NC}" | tee -a $RESULTS_FILE
TOTAL=$((PASSED + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))
echo "Success Rate: $PERCENTAGE%" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

if [ $PERCENTAGE -ge 80 ]; then
    echo -e "${GREEN}✅ SYSTEM READY FOR PILOT${NC}" | tee -a $RESULTS_FILE
elif [ $PERCENTAGE -ge 60 ]; then
    echo -e "${YELLOW}⚠️  SYSTEM PARTIALLY READY - Review failures${NC}" | tee -a $RESULTS_FILE
else
    echo -e "${RED}❌ SYSTEM NOT READY - Critical issues detected${NC}" | tee -a $RESULTS_FILE
fi

echo "" | tee -a $RESULTS_FILE
echo "Completed: $(date)" | tee -a $RESULTS_FILE
echo "Results saved to: $RESULTS_FILE" | tee -a $RESULTS_FILE
