#!/bin/bash

# AWS EC2 Private GPT System Auto-Recovery Script
# This script automatically restarts services and fixes common issues

set -e

echo "==========================================="
echo "Private GPT System Auto-Recovery"
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
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run remote command
run_remote() {
    ssh -i "$SSH_KEY" "$SSH_USER@$EC2_HOST" "$1"
}

# Function to run remote command silently
run_remote_silent() {
    ssh -i "$SSH_KEY" "$SSH_USER@$EC2_HOST" "$1" > /dev/null 2>&1
}

echo -e "${BLUE}Step 1: Verifying EC2 instance is reachable...${NC}"
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$SSH_USER@$EC2_HOST" "echo 'Connected'" > /dev/null 2>&1; then
    echo -e "${RED}✗ Cannot connect to EC2 instance${NC}"
    echo ""
    echo "Please ensure:"
    echo "1. Instance is started in AWS Console"
    echo "2. Instance public IP is: $EC2_HOST"
    echo "3. Security group allows SSH (port 22) from your IP"
    echo ""
    echo "To start instance from AWS CLI:"
    echo "aws ec2 start-instances --instance-ids <your-instance-id>"
    exit 1
fi
echo -e "${GREEN}✓ EC2 instance is reachable${NC}"

echo ""
echo -e "${BLUE}Step 2: Checking and fixing backend service...${NC}"

# Stop the backend service first
echo "   Stopping backend service..."
run_remote_silent "sudo systemctl stop privategpt-backend"

# Kill any orphaned uvicorn processes
echo "   Cleaning up orphaned processes..."
run_remote_silent "sudo pkill -f uvicorn || true"
run_remote_silent "sudo pkill -f 'python.*main:app' || true"

# Clear any stale pid files
run_remote_silent "sudo rm -f /var/run/privategpt-backend.pid"

# Ensure environment file exists
echo "   Verifying environment configuration..."
ENV_EXISTS=$(run_remote "test -f /home/ec2-user/privategpt-backend/.env && echo 'yes' || echo 'no'")
if [ "$ENV_EXISTS" = "no" ]; then
    echo -e "${YELLOW}   ⚠ Environment file missing, creating from backup...${NC}"
    run_remote "cp /home/ec2-user/privategpt-backend/.env.backup /home/ec2-user/privategpt-backend/.env 2>/dev/null || echo 'No backup found'"
fi

# Start the backend service
echo "   Starting backend service..."
run_remote "sudo systemctl start privategpt-backend"
sleep 3

# Check if it started successfully
BACKEND_STATUS=$(run_remote "sudo systemctl is-active privategpt-backend 2>/dev/null || echo 'inactive'")
if [ "$BACKEND_STATUS" = "active" ]; then
    echo -e "${GREEN}✓ Backend service started successfully${NC}"
else
    echo -e "${RED}✗ Backend service failed to start${NC}"
    echo "   Recent logs:"
    run_remote "sudo journalctl -u privategpt-backend -n 20 --no-pager"
fi

echo ""
echo -e "${BLUE}Step 3: Checking and fixing Nginx...${NC}"

# Test nginx configuration
echo "   Testing Nginx configuration..."
NGINX_TEST=$(run_remote "sudo nginx -t 2>&1 | grep -c 'syntax is ok' || echo '0'")
if [ "$NGINX_TEST" = "1" ]; then
    echo -e "${GREEN}   ✓ Nginx configuration is valid${NC}"
else
    echo -e "${RED}   ✗ Nginx configuration has errors${NC}"
    run_remote "sudo nginx -t"
fi

# Restart nginx
echo "   Restarting Nginx..."
run_remote "sudo systemctl restart nginx"

NGINX_STATUS=$(run_remote "sudo systemctl is-active nginx 2>/dev/null || echo 'inactive'")
if [ "$NGINX_STATUS" = "active" ]; then
    echo -e "${GREEN}✓ Nginx restarted successfully${NC}"
else
    echo -e "${RED}✗ Nginx failed to start${NC}"
fi

echo ""
echo -e "${BLUE}Step 4: Verifying API endpoints...${NC}"

# Wait for services to stabilize
sleep 2

# Test backend health endpoint directly
echo "   Testing backend API directly..."
BACKEND_HEALTH=$(run_remote "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/health 2>/dev/null || echo '000'")
if [ "$BACKEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}   ✓ Backend API responding on port 8000${NC}"
else
    echo -e "${RED}   ✗ Backend API not responding (HTTP $BACKEND_HEALTH)${NC}"
fi

# Test through nginx proxy
echo "   Testing API through Nginx proxy..."
PROXY_HEALTH=$(curl -k -s -o /dev/null -w '%{http_code}' "https://$EC2_HOST/api/health" 2>/dev/null || echo '000')
if [ "$PROXY_HEALTH" = "200" ]; then
    echo -e "${GREEN}   ✓ Nginx proxy working correctly${NC}"
else
    echo -e "${RED}   ✗ Nginx proxy not working (HTTP $PROXY_HEALTH)${NC}"
fi

echo ""
echo -e "${BLUE}Step 5: Testing Pinecone vector database...${NC}"
VECTOR_COUNT=$(run_remote "cd /home/ec2-user/privategpt-backend && python3 -c '
from app.services.vector_service import VectorService
import asyncio
try:
    vs = VectorService()
    stats = vs.index.describe_index_stats()
    print(stats.total_vector_count)
except:
    print(0)
' 2>/dev/null || echo '0'")

if [ "$VECTOR_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Pinecone connected with $VECTOR_COUNT vectors${NC}"
else
    echo -e "${YELLOW}⚠ Pinecone has no vectors or connection failed${NC}"
    echo "   You may need to re-ingest documents"
fi

echo ""
echo -e "${BLUE}Step 6: Testing chat functionality...${NC}"
CHAT_RESPONSE=$(curl -k -s -X POST "https://$EC2_HOST/api/chat/" \
    -H "Content-Type: application/json" \
    -d '{"message":"Hello","session_id":"test-recovery"}' 2>/dev/null)

if echo "$CHAT_RESPONSE" | grep -q "response"; then
    echo -e "${GREEN}✓ Chat API is functional${NC}"
else
    echo -e "${RED}✗ Chat API not responding correctly${NC}"
    echo "   Response: $CHAT_RESPONSE"
fi

echo ""
echo -e "${BLUE}Step 7: Clearing potential issues...${NC}"

# Clear any stale session data
echo "   Clearing stale sessions..."
run_remote_silent "sudo rm -rf /tmp/privategpt-sessions/*"

# Ensure log directory exists with correct permissions
echo "   Fixing log permissions..."
run_remote_silent "sudo mkdir -p /var/log/privategpt"
run_remote_silent "sudo chown ec2-user:ec2-user /var/log/privategpt"

# Clear old logs if they're too large
LOG_SIZE=$(run_remote "du -sm /var/log/privategpt 2>/dev/null | cut -f1 || echo '0'")
if [ "$LOG_SIZE" -gt 100 ]; then
    echo "   Rotating large logs ($LOG_SIZE MB)..."
    run_remote_silent "sudo logrotate -f /etc/logrotate.d/privategpt 2>/dev/null || true"
fi

echo ""
echo "==========================================="
echo -e "${GREEN}Recovery Process Complete!${NC}"
echo "==========================================="
echo ""
echo "System Status:"
echo "--------------"

# Final status check
BACKEND_FINAL=$(run_remote "sudo systemctl is-active privategpt-backend 2>/dev/null || echo 'inactive'")
NGINX_FINAL=$(run_remote "sudo systemctl is-active nginx 2>/dev/null || echo 'inactive'")
API_FINAL=$(curl -k -s -o /dev/null -w '%{http_code}' "https://$EC2_HOST/api/health" 2>/dev/null || echo '000')

if [ "$BACKEND_FINAL" = "active" ]; then
    echo -e "Backend Service: ${GREEN}Active${NC}"
else
    echo -e "Backend Service: ${RED}$BACKEND_FINAL${NC}"
fi

if [ "$NGINX_FINAL" = "active" ]; then
    echo -e "Nginx Service:   ${GREEN}Active${NC}"
else
    echo -e "Nginx Service:   ${RED}$NGINX_FINAL${NC}"
fi

if [ "$API_FINAL" = "200" ]; then
    echo -e "API Status:      ${GREEN}Healthy${NC}"
else
    echo -e "API Status:      ${RED}Not responding (HTTP $API_FINAL)${NC}"
fi

echo -e "Vector Database: ${GREEN}$VECTOR_COUNT vectors${NC}"

echo ""
echo "Access your Private GPT at:"
echo -e "${BLUE}https://$EC2_HOST/${NC}"
echo ""
echo "Note: You'll need to accept the self-signed certificate warning"
echo ""

if [ "$BACKEND_FINAL" != "active" ] || [ "$API_FINAL" != "200" ]; then
    echo -e "${YELLOW}⚠ Some issues remain. Check logs with:${NC}"
    echo "ssh -i $SSH_KEY $SSH_USER@$EC2_HOST 'sudo journalctl -u privategpt-backend -f'"
    echo ""
fi

echo "For real-time monitoring:"
echo "ssh -i $SSH_KEY $SSH_USER@$EC2_HOST 'sudo tail -f /var/log/privategpt/app.log'"
echo ""
