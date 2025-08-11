#!/bin/bash

# Setup script for Private GPT on Amazon Linux 2023
set -e

echo "=== Starting Private GPT Setup on Amazon Linux ==="

# Update system
echo "1. Updating system packages..."
sudo yum update -y

# Install Python dependencies
echo "2. Installing Python and pip..."
sudo yum install -y python3-pip python3-devel gcc

# Install Node.js 18
echo "3. Installing Node.js..."
curl -sL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Install nginx
echo "4. Installing Nginx..."
sudo yum install -y nginx

# Create project directory
echo "5. Setting up project..."
mkdir -p ~/privategpt
cd ~/privategpt

# Extract deployment package
tar -xzf ~/privategpt-deployment.tar.gz

# Setup Python virtual environment
echo "6. Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install fastapi uvicorn python-multipart python-dotenv aiofiles
pip install boto3 pinecone-client tiktoken

# Setup frontend
echo "7. Building frontend..."
npm install
npm run build

# Create environment file
echo "8. Creating environment configuration..."
cat > backend/.env << 'EOF'
# AWS Bedrock Configuration
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.titan-text-express-v1
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=legal-docs-1024
PINECONE_ENVIRONMENT=gcp-starter

# Server Configuration
HOST=0.0.0.0
PORT=8000
EOF

echo "Please update the .env file with your actual API keys!"

# Setup systemd service for backend
echo "9. Creating systemd service for backend..."
sudo tee /etc/systemd/system/privategpt-backend.service > /dev/null << 'EOF'
[Unit]
Description=Private GPT Backend
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/privategpt/backend
Environment="PATH=/home/ec2-user/privategpt/venv/bin"
ExecStart=/home/ec2-user/privategpt/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Setup nginx configuration
echo "10. Configuring Nginx..."
sudo tee /etc/nginx/conf.d/privategpt.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        root /home/ec2-user/privategpt/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
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
EOF

# Start services
echo "11. Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable privategpt-backend
sudo systemctl start privategpt-backend
sudo systemctl enable nginx
sudo systemctl restart nginx

# Open firewall ports
echo "12. Configuring firewall..."
sudo firewall-cmd --zone=public --add-port=80/tcp --permanent 2>/dev/null || true
sudo firewall-cmd --reload 2>/dev/null || true

echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit /home/ec2-user/privategpt/backend/.env with your API keys"
echo "2. Restart the backend: sudo systemctl restart privategpt-backend"
echo "3. Access your Private GPT at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "Check service status:"
echo "  sudo systemctl status privategpt-backend"
echo "  sudo systemctl status nginx"
echo ""
echo "View logs:"
echo "  sudo journalctl -u privategpt-backend -f"
