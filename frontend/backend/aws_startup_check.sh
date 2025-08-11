#!/bin/bash

# AWS EC2 Private GPT System Startup Checklist and Diagnostic Script
# Run this after bringing up your EC2 instance to verify all services

set -e

echo "==========================================="
echo "Private GPT System Startup Check"
echo "==========================================="
echo ""

# Get IP from parameter, stdin, or prompt
if [ -n "$1" ]; then
    EC2_HOST="$1"
elif [ ! -t 0 ]; then
    # Read from stdin if available
    read EC2_HOST
else
    # Prompt for EC2 IP address
    echo "Enter your EC2 instance public IP address:"
    echo "(You can find this in AWS Console under EC2 > Instances)"
    read -p "IP Address: " EC2_HOST
fi

# Validate IP address format
if [[ ! $EC2_HOST =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    echo "Invalid IP address format: $EC2_HOST"
    exit 1
fi

# Configuration
SSH_KEY="$HOME/.ssh/Scott-Key.pem"
SSH_USER="ec2-user"

echo ""
echo "Using EC2 instance at: $EC2_HOST"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check status
check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        return 1
    fi
}

# Function to run remote command
run_remote() {
    ssh -i "$SSH_KEY" "$SSH_USER@$EC2_HOST" "$1"
}

echo "1. Checking SSH connectivity..."
if ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$SSH_USER@$EC2_HOST" "echo 'SSH connection successful'" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} SSH connection established"
else
    echo -e "${RED}✗${NC} Cannot connect via SSH. Please check:"
    echo "   - Instance is running in AWS Console"
    echo "   - Security group allows SSH (port 22)"
    echo "   - Public IP is correct: $EC2_HOST"
    exit 1
fi

echo ""
echo "2. Checking system services..."

# Check backend service
echo -n "   Backend service (privategpt-backend): "
BACKEND_STATUS=$(run_remote "sudo systemctl is-active privategpt-backend 2>/dev/null || echo 'inactive'")
if [ "$BACKEND_STATUS" = "active" ]; then
    echo -e "${GREEN}Active${NC}"
else
    echo -e "${RED}$BACKEND_STATUS${NC}"
    echo "   To start: ssh -i $SSH_KEY $SSH_USER@$EC2_HOST 'sudo systemctl start privategpt-backend'"
fi

# Check nginx
echo -n "   Nginx service: "
NGINX_STATUS=$(run_remote "sudo systemctl is-active nginx 2>/dev/null || echo 'inactive'")
if [ "$NGINX_STATUS" = "active" ]; then
    echo -e "${GREEN}Active${NC}"
else
    echo -e "${RED}$NGINX_STATUS${NC}"
    echo "   To start: ssh -i $SSH_KEY $SSH_USER@$EC2_HOST 'sudo systemctl start nginx'"
fi

echo ""
echo "3. Checking backend API health..."
# Check backend directly on port 8000
BACKEND_HEALTH=$(run_remote "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/health 2>/dev/null || echo '000'")
if [ "$BACKEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓${NC} Backend API responding on port 8000"
else
    echo -e "${RED}✗${NC} Backend API not responding (HTTP $BACKEND_HEALTH)"
    echo "   Checking logs..."
    run_remote "sudo journalctl -u privategpt-backend -n 10 --no-pager" 2>/dev/null || echo "   Could not retrieve logs"
fi

echo ""
echo "4. Checking Nginx proxy..."
# Check nginx proxy to backend
PROXY_HEALTH=$(curl -k -s -o /dev/null -w '%{http_code}' "https://$EC2_HOST/api/health" 2>/dev/null || echo '000')
if [ "$PROXY_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓${NC} Nginx proxy to backend working"
else
    echo -e "${RED}✗${NC} Nginx proxy not working (HTTP $PROXY_HEALTH)"
fi

echo ""
echo "5. Checking frontend..."
FRONTEND_STATUS=$(curl -k -s -o /dev/null -w '%{http_code}' "https://$EC2_HOST/" 2>/dev/null || echo '000')
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓${NC} Frontend accessible"
else
    echo -e "${YELLOW}⚠${NC} Frontend returned HTTP $FRONTEND_STATUS"
fi

echo ""
echo "6. Checking environment variables..."
ENV_CHECK=$(run_remote "cat /home/ec2-user/privategpt-backend/.env 2>/dev/null | grep -c '=' || echo '0'")
if [ "$ENV_CHECK" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Environment file exists with $ENV_CHECK variables"
    echo "   Key variables:"
    run_remote "cat /home/ec2-user/privategpt-backend/.env | grep -E '^(AWS_REGION|BEDROCK_MODEL_ID|PINECONE_INDEX_NAME)' | sed 's/=.*/=***/' | sed 's/^/      /'"
else
    echo -e "${RED}✗${NC} Environment file missing or empty"
fi

echo ""
echo "7. Checking Pinecone connection..."
PINECONE_TEST=$(run_remote "cd /home/ec2-user/privategpt-backend && python3 -c 'from app.services.vector_service import VectorService; import asyncio; vs = VectorService(); print(\"OK\" if vs.index else \"FAIL\")' 2>/dev/null || echo 'ERROR'")
if [ "$PINECONE_TEST" = "OK" ]; then
    echo -e "${GREEN}✓${NC} Pinecone connection established"
else
    echo -e "${RED}✗${NC} Pinecone connection failed"
fi

echo ""
echo "8. Testing chat endpoint..."
CHAT_TEST=$(curl -k -s -X POST "https://$EC2_HOST/api/chat/" \
    -H "Content-Type: application/json" \
    -d '{"message":"Hello","session_id":"test"}' \
    -w '\n%{http_code}' 2>/dev/null | tail -1)
if [ "$CHAT_TEST" = "200" ]; then
    echo -e "${GREEN}✓${NC} Chat API responding correctly"
else
    echo -e "${RED}✗${NC} Chat API returned HTTP $CHAT_TEST"
fi

echo ""
echo "==========================================="
echo "QUICK FIX COMMANDS:"
echo "==========================================="
echo ""
echo "# Connect to instance:"
echo "ssh -i $SSH_KEY $SSH_USER@$EC2_HOST"
echo ""
echo "# Restart all services:"
echo "ssh -i $SSH_KEY $SSH_USER@$EC2_HOST 'sudo systemctl restart privategpt-backend nginx'"
echo ""
echo "# Check backend logs:"
echo "ssh -i $SSH_KEY $SSH_USER@$EC2_HOST 'sudo journalctl -u privategpt-backend -f'"
echo ""
echo "# Check nginx logs:"
echo "ssh -i $SSH_KEY $SSH_USER@$EC2_HOST 'sudo tail -f /var/log/nginx/error.log'"
echo ""
echo "# Test backend directly:"
echo "ssh -i $SSH_KEY $SSH_USER@$EC2_HOST 'curl http://localhost:8000/api/health'"
echo ""
echo "# Access the UI:"
echo "https://$EC2_HOST/"
echo ""
