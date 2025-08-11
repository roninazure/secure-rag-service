#!/bin/bash

# AWS EC2 Deployment Sync Script
# Purpose: Ensure AWS deployment matches MacBook configuration exactly
# Author: Scott Steele System
# Date: December 2024

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
KEY_PATH="$HOME/.ssh/Scott-Key.pem"
LOCAL_BACKEND_PATH="/Users/scottsteele/privategpt-ui/backend"
LOCAL_FRONTEND_PATH="/Users/scottsteele/privategpt-ui"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AWS EC2 Private GPT Deployment Sync${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to check if EC2 instance is reachable
check_ec2_connection() {
    local ip=$1
    echo -e "${YELLOW}Testing connection to EC2 instance at $ip...${NC}"
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i "$KEY_PATH" ec2-user@"$ip" "echo 'Connected'" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Successfully connected to EC2 instance${NC}"
        return 0
    else
        echo -e "${RED}✗ Cannot connect to EC2 instance${NC}"
        return 1
    fi
}

# Get EC2 IP
if [ -z "$1" ]; then
    echo -e "${YELLOW}Please enter your EC2 instance public IP address:${NC}"
    read -r EC2_IP
else
    EC2_IP=$1
fi

# Validate connection
if ! check_ec2_connection "$EC2_IP"; then
    echo -e "${RED}Cannot proceed without EC2 connection${NC}"
    exit 1
fi

echo -e "${GREEN}Connected to EC2 at $EC2_IP${NC}"

# Create deployment package with exact MacBook configuration
echo -e "${BLUE}Creating deployment package...${NC}"

# Create temp directory for deployment
TEMP_DIR=$(mktemp -d)
DEPLOY_DIR="$TEMP_DIR/privategpt-deploy"
mkdir -p "$DEPLOY_DIR"

# Copy backend files
echo -e "${YELLOW}Copying backend files...${NC}"
cp -r "$LOCAL_BACKEND_PATH/app" "$DEPLOY_DIR/"
cp "$LOCAL_BACKEND_PATH/requirements.txt" "$DEPLOY_DIR/" 2>/dev/null || true
cp "$LOCAL_BACKEND_PATH/.env" "$DEPLOY_DIR/"

# Copy frontend build (if exists)
if [ -d "$LOCAL_FRONTEND_PATH/dist" ]; then
    echo -e "${YELLOW}Copying frontend build...${NC}"
    cp -r "$LOCAL_FRONTEND_PATH/dist" "$DEPLOY_DIR/frontend"
fi

# Create requirements.txt if it doesn't exist
if [ ! -f "$DEPLOY_DIR/requirements.txt" ]; then
    echo -e "${YELLOW}Creating requirements.txt...${NC}"
    cat > "$DEPLOY_DIR/requirements.txt" << 'EOF'
fastapi==0.116.1
uvicorn[standard]==0.35.0
python-dotenv==1.1.1
boto3==1.40.3
pinecone[grpc]==7.3.0
python-multipart==0.0.20
httpx==0.28.1
aiofiles==24.1.0
pydantic==2.10.6
EOF
fi

# Create deployment script
cat > "$DEPLOY_DIR/deploy.sh" << 'DEPLOY_SCRIPT'
#!/bin/bash

# AWS EC2 Deployment Script
set -e

echo "Starting deployment on EC2..."

# Update system
sudo yum update -y

# Install Python 3.11 if not present
if ! command -v python3.11 &> /dev/null; then
    echo "Installing Python 3.11..."
    sudo yum install -y python3.11 python3.11-pip
fi

# Install Node.js if not present (for frontend)
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -sL https://rpm.nodesource.com/setup_18.x | sudo bash -
    sudo yum install -y nodejs
fi

# Install nginx if not present
if ! command -v nginx &> /dev/null; then
    echo "Installing nginx..."
    sudo yum install -y nginx
fi

# Setup backend
echo "Setting up backend..."
cd /home/ec2-user

# Stop existing backend service
sudo systemctl stop privategpt-backend 2>/dev/null || true

# Remove old backend directory
rm -rf privategpt-backend-old
[ -d privategpt-backend ] && mv privategpt-backend privategpt-backend-old

# Create new backend directory
mkdir -p privategpt-backend
cp -r /tmp/deploy/app privategpt-backend/
cp /tmp/deploy/.env privategpt-backend/
cp /tmp/deploy/requirements.txt privategpt-backend/

# Create virtual environment
cd privategpt-backend
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service for backend
sudo tee /etc/systemd/system/privategpt-backend.service > /dev/null << 'SERVICE'
[Unit]
Description=PrivateGPT Backend API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/privategpt-backend
Environment="PATH=/home/ec2-user/privategpt-backend/venv/bin"
ExecStart=/home/ec2-user/privategpt-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Setup frontend (if provided)
if [ -d /tmp/deploy/frontend ]; then
    echo "Setting up frontend..."
    sudo rm -rf /usr/share/nginx/html/*
    sudo cp -r /tmp/deploy/frontend/* /usr/share/nginx/html/
    sudo chown -R nginx:nginx /usr/share/nginx/html
fi

# Configure nginx
sudo tee /etc/nginx/conf.d/privategpt.conf > /dev/null << 'NGINX'
server {
    listen 80;
    server_name _;
    
    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API proxy
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl;
    server_name _;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API proxy
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

# Create SSL certificate if not exists
if [ ! -f /etc/nginx/ssl/cert.pem ]; then
    sudo mkdir -p /etc/nginx/ssl
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/key.pem \
        -out /etc/nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

# Reload systemd and start services
sudo systemctl daemon-reload
sudo systemctl enable privategpt-backend
sudo systemctl start privategpt-backend
sudo systemctl enable nginx
sudo systemctl restart nginx

echo "Deployment complete!"
echo "Backend status:"
sudo systemctl status privategpt-backend --no-pager | head -10
echo ""
echo "Testing backend health..."
sleep 5
curl -s http://localhost:8000/api/health || echo "Backend not responding yet"
DEPLOY_SCRIPT

chmod +x "$DEPLOY_DIR/deploy.sh"

# Create tarball
echo -e "${YELLOW}Creating deployment archive...${NC}"
cd "$TEMP_DIR"
tar -czf privategpt-deploy.tar.gz privategpt-deploy/

# Upload to EC2
echo -e "${BLUE}Uploading to EC2...${NC}"
scp -i "$KEY_PATH" privategpt-deploy.tar.gz ec2-user@"$EC2_IP":/tmp/

# Deploy on EC2
echo -e "${BLUE}Running deployment on EC2...${NC}"
ssh -i "$KEY_PATH" ec2-user@"$EC2_IP" << 'REMOTE_COMMANDS'
set -e
cd /tmp
rm -rf deploy
tar -xzf privategpt-deploy.tar.gz
mv privategpt-deploy deploy
cd deploy
chmod +x deploy.sh
./deploy.sh
REMOTE_COMMANDS

# Cleanup
rm -rf "$TEMP_DIR"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Sync Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Test the backend API: https://$EC2_IP/api/health"
echo "2. Test the frontend: https://$EC2_IP"
echo "3. Run document ingestion script"
echo ""
echo -e "${BLUE}To ingest documents, run:${NC}"
echo "  ./aws_ingest_documents.sh $EC2_IP"
