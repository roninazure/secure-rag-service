#!/bin/bash

# Interactive Demo Script for Monday Presentation
# This walks through key features for stakeholders

API_URL="https://44.202.131.48/api"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}   Private GPT Demo - Legal Assistant    ${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo "This demo will showcase the system's capabilities"
echo "Press Enter after each query to continue..."
echo ""

# Function to run demo query
demo_query() {
    local category="$1"
    local query="$2"
    local explanation="$3"
    
    echo -e "${YELLOW}Category: $category${NC}"
    echo -e "${GREEN}Query:${NC} $query"
    echo ""
    echo "Expected: $explanation"
    echo ""
    echo "Sending query..."
    echo ""
    
    response=$(curl -s -X POST "$API_URL/chat/" \
        -H "Content-Type: application/json" \
        -H "User-Agent: Demo-$$" \
        -k \
        -d "{\"message\":\"$query\"}" 2>/dev/null | \
        python3 -c "import sys, json; print(json.load(sys.stdin).get('content', 'No response'))" 2>/dev/null)
    
    echo -e "${BLUE}Response:${NC}"
    echo "$response" | fold -w 80 -s
    echo ""
    echo "----------------------------------------"
    read -p "Press Enter to continue..."
    clear
}

# Demo Introduction
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}        DEMO 1: HR POLICIES              ${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
read -p "Press Enter to start HR demos..."
clear

demo_query "HR - Remote Work" \
    "What is our remote work policy?" \
    "Should explain supervisor approval requirements and eligibility"

demo_query "HR - Time Off" \
    "How much PTO do employees get after 5 years?" \
    "Should show 20 days per year for years 4-6"

demo_query "HR - Benefits" \
    "What equipment does the firm provide for remote workers?" \
    "Should list laptop, VPN access, software licenses"

# Billing Demos
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}        DEMO 2: BILLING & RATES          ${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
read -p "Press Enter to start billing demos..."
clear

demo_query "Billing - Partner Rates" \
    "What are the hourly rates for equity partners?" \
    "Should show $850-1,200 per hour range"

demo_query "Billing - Retainer" \
    "What is the standard retainer amount for new clients?" \
    "Should mention $10,000 initial retainer"

demo_query "Billing - Practices" \
    "What is the minimum billing increment?" \
    "Should explain 6-minute (0.1 hour) increments"

# Legal Practice Demos
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}      DEMO 3: LEGAL PRACTICE AREAS       ${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
read -p "Press Enter to start legal practice demos..."
clear

demo_query "Criminal Defense" \
    "What types of criminal cases does the firm handle?" \
    "Should list white collar, federal, state felonies, etc."

demo_query "Litigation Process" \
    "What are the main phases of civil litigation?" \
    "Should outline complaint, discovery, trial phases"

demo_query "Document Preservation" \
    "What is a litigation hold and what does it require?" \
    "Should explain preservation requirements and obligations"

# Conversation Context Demo
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}    DEMO 4: CONVERSATION CONTINUITY      ${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo "This demonstrates the system maintains context"
echo ""
read -p "Press Enter to start conversation demo..."
clear

SESSION="Demo-Context-$$"

echo -e "${YELLOW}First Query:${NC}"
echo "What are the different types of legal services we offer?"
echo ""
curl -s -X POST "$API_URL/chat/" \
    -H "Content-Type: application/json" \
    -H "User-Agent: $SESSION" \
    -k \
    -d '{"message":"What are the different types of legal services we offer?"}' | \
    python3 -c "import sys, json; print(json.load(sys.stdin).get('content', ''))" | fold -w 80 -s

echo ""
read -p "Press Enter for follow-up question..."
echo ""

echo -e "${YELLOW}Follow-up Query (using context):${NC}"
echo "Tell me more about the criminal defense services"
echo ""
curl -s -X POST "$API_URL/chat/" \
    -H "Content-Type: application/json" \
    -H "User-Agent: $SESSION" \
    -k \
    -d '{"message":"Tell me more about the criminal defense services"}' | \
    python3 -c "import sys, json; print(json.load(sys.stdin).get('content', ''))" | fold -w 80 -s

echo ""
echo "----------------------------------------"
echo ""

# Summary
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}           DEMO COMPLETE                 ${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "Key Features Demonstrated:"
echo "✅ Domain-specific knowledge (HR, Legal, Billing)"
echo "✅ Accurate information retrieval"
echo "✅ Conversation context maintenance"
echo "✅ Professional responses"
echo ""
echo "System URL: https://44.202.131.48"
echo ""
echo "Note: Users will see a browser security warning"
echo "      (Click Advanced → Proceed to continue)"
echo ""
