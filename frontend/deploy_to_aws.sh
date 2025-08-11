#!/bin/bash

# Private GPT AWS EC2 Deployment Script
# For: t3.micro Ubuntu instance in us-east-1
# This script sets up the complete Private GPT stack on a fresh EC2 instance

set -e  # Exit on error

echo "🚀 Private GPT AWS EC2 Deployment Script"
echo "========================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on EC2
if [ ! -f /sys/hypervisor/uuid ] || [ $(head -c 3 /sys/hypervisor/uuid) != "ec2" ]; then
    echo -e "${YELLOW}Warning: This doesn't appear to be an EC2 instance${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}Step 1: System Updates${NC}"
echo "------------------------"
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y curl wget git build-essential software-properties-common

echo -e "${GREEN}Step 2: Install Python 3.11${NC}"
echo "----------------------------"
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

echo -e "${GREEN}Step 3: Install Node.js 18+ for Frontend${NC}"
echo "-----------------------------------------"
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

echo -e "${GREEN}Step 4: Install Nginx${NC}"
echo "----------------------"
sudo apt-get install -y nginx
sudo systemctl enable nginx

echo -e "${GREEN}Step 5: Clone Private GPT Repository${NC}"
echo "-------------------------------------"
cd /home/ubuntu
if [ -d "privategpt-ui" ]; then
    echo "Repository already exists, pulling latest..."
    cd privategpt-ui
    git pull
else
    git clone https://github.com/yourusername/privategpt-ui.git
    cd privategpt-ui
fi

echo -e "${GREEN}Step 6: Setup Python Virtual Environment${NC}"
echo "-----------------------------------------"
cd /home/ubuntu/privategpt-ui/backend
python3.11 -m venv venv
source venv/bin/activate

echo -e "${GREEN}Step 7: Install Python Dependencies${NC}"
echo "------------------------------------"
pip install --upgrade pip
pip install fastapi uvicorn python-dotenv boto3 pinecone langchain pydantic python-multipart tiktoken

echo -e "${GREEN}Step 8: Build Frontend${NC}"
echo "-----------------------"
cd /home/ubuntu/privategpt-ui/frontend
npm install
npm run build

echo -e "${GREEN}Step 9: Configure Nginx${NC}"
echo "------------------------"
sudo tee /etc/nginx/sites-available/privategpt > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    # Frontend - serve React build
    location / {
        root /home/ubuntu/privategpt-ui/frontend/dist;
        try_files \$uri \$uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }
    
    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts for AI responses
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/privategpt /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo -e "${GREEN}Step 10: Create Systemd Service for Backend${NC}"
echo "--------------------------------------------"
sudo tee /etc/systemd/system/privategpt-backend.service > /dev/null <<EOF
[Unit]
Description=Private GPT FastAPI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/privategpt-ui/backend
Environment="PATH=/home/ubuntu/privategpt-ui/backend/venv/bin"
ExecStart=/home/ubuntu/privategpt-ui/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/privategpt/backend.log
StandardError=append:/var/log/privategpt/backend-error.log

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
sudo mkdir -p /var/log/privategpt
sudo chown ubuntu:ubuntu /var/log/privategpt

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable privategpt-backend

echo -e "${GREEN}Step 11: Setup Environment Variables${NC}"
echo "-------------------------------------"
echo -e "${YELLOW}Creating .env template file...${NC}"

cat > /home/ubuntu/privategpt-ui/backend/.env.template <<EOF
# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.titan-text-express-v1
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=privategpt-index
PINECONE_ENVIRONMENT=us-east-1

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=["*"]
EOF

echo -e "${RED}IMPORTANT: Configure your environment variables!${NC}"
echo "1. Copy the template: cp /home/ubuntu/privategpt-ui/backend/.env.template /home/ubuntu/privategpt-ui/backend/.env"
echo "2. Edit with your actual credentials: nano /home/ubuntu/privategpt-ui/backend/.env"
echo "3. Start the backend: sudo systemctl start privategpt-backend"

echo -e "${GREEN}Step 12: Setup Firewall (UFW)${NC}"
echo "-------------------------------"
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw --force enable

echo -e "${GREEN}Step 13: Create Monitoring Script${NC}"
echo "----------------------------------"
cat > /home/ubuntu/check_privategpt.sh <<'EOF'
#!/bin/bash
echo "Private GPT System Status"
echo "========================="
echo ""
echo "Backend Service:"
sudo systemctl status privategpt-backend --no-pager | head -n 10
echo ""
echo "Nginx Status:"
sudo systemctl status nginx --no-pager | head -n 5
echo ""
echo "API Health Check:"
curl -s http://localhost:8000/health || echo "Backend not responding"
echo ""
echo "Recent Backend Logs:"
tail -n 10 /var/log/privategpt/backend.log 2>/dev/null || echo "No logs yet"
echo ""
echo "Disk Usage:"
df -h /
echo ""
echo "Memory Usage:"
free -h
EOF

chmod +x /home/ubuntu/check_privategpt.sh

echo ""
echo "========================================"
echo -e "${GREEN}✅ AWS EC2 Setup Complete!${NC}"
echo "========================================"
echo ""
echo "Next Steps:"
echo "1. Configure environment variables:"
echo "   cp /home/ubuntu/privategpt-ui/backend/.env.template /home/ubuntu/privategpt-ui/backend/.env"
echo "   nano /home/ubuntu/privategpt-ui/backend/.env"
echo ""
echo "2. Start the backend service:"
echo "   sudo systemctl start privategpt-backend"
echo ""
echo "3. Check system status:"
echo "   ./check_privategpt.sh"
echo ""
echo "4. Access your Private GPT:"
echo "   http://YOUR_EC2_PUBLIC_IP"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u privategpt-backend -f"
echo ""
echo -e "${YELLOW}Remember: Update security group to allow HTTP (80) access!${NC}"
