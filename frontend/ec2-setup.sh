#!/bin/bash

# EC2 RAG System Setup Script
# For t2.micro Ubuntu instance with IAM role

set -e  # Exit on error

echo "==================================="
echo "RAG System EC2 Deployment Script"
echo "==================================="

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.11 and pip
echo "Installing Python 3.11..."
sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Install Node.js 20.x
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Nginx
echo "Installing Nginx..."
sudo apt-get install -y nginx

# Install additional dependencies
echo "Installing system dependencies..."
sudo apt-get install -y build-essential git curl wget unzip

# Create application directory
echo "Setting up application directory..."
sudo mkdir -p /opt/rag-app
sudo chown ubuntu:ubuntu /opt/rag-app

# Extract deployment package
echo "Extracting application files..."
cd /opt/rag-app
tar -xzf ~/rag-deployment-new.tar.gz

# Setup Python virtual environment
echo "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
boto3==1.34.23
pinecone==5.3.1
pydantic==2.5.3
python-multipart==0.0.6
tiktoken==0.5.2
langchain==0.1.0
langchain-community==0.0.10
EOF

pip install --upgrade pip
pip install -r requirements.txt

# Create .env file with IAM role configuration
echo "Creating environment configuration..."
cat > /opt/rag-app/backend/.env << 'EOF'
# AWS Configuration (IAM role will provide credentials)
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.titan-text-express-v1
BEDROCK_EMBED_MODEL_ID=amazon.titan-embed-text-v1

# Pinecone Configuration
PINECONE_API_KEY=${PINECONE_API_KEY}
PINECONE_ENVIRONMENT=${PINECONE_ENVIRONMENT}
PINECONE_INDEX_NAME=rag-index

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
EOF

# Build frontend
echo "Building frontend..."
cd /opt/rag-app
npm install
npm run build

# Create systemd service for backend
echo "Creating systemd service..."
sudo tee /etc/systemd/system/rag-backend.service > /dev/null << 'EOF'
[Unit]
Description=RAG Backend Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/rag-app/backend
Environment="PATH=/opt/rag-app/venv/bin"
ExecStart=/opt/rag-app/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/rag-app > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        root /opt/rag-app/dist;
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

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/rag-app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Start and enable backend service
echo "Starting backend service..."
sudo systemctl daemon-reload
sudo systemctl enable rag-backend
sudo systemctl start rag-backend

# Create monitoring script
echo "Creating monitoring script..."
cat > /opt/rag-app/monitor.sh << 'EOF'
#!/bin/bash
echo "=== RAG System Status ==="
echo ""
echo "Backend Service:"
sudo systemctl status rag-backend --no-pager | head -10
echo ""
echo "Nginx Service:"
sudo systemctl status nginx --no-pager | head -10
echo ""
echo "API Health Check:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo "Recent Backend Logs:"
sudo journalctl -u rag-backend -n 20 --no-pager
EOF
chmod +x /opt/rag-app/monitor.sh

# Create update script
echo "Creating update script..."
cat > /opt/rag-app/update.sh << 'EOF'
#!/bin/bash
cd /opt/rag-app
source venv/bin/activate
git pull || echo "Manual file update needed"
pip install -r requirements.txt
npm install
npm run build
sudo systemctl restart rag-backend
sudo systemctl restart nginx
echo "Update complete!"
EOF
chmod +x /opt/rag-app/update.sh

# Setup log rotation
echo "Setting up log rotation..."
sudo tee /etc/logrotate.d/rag-app > /dev/null << 'EOF'
/var/log/rag-app/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload rag-backend >/dev/null 2>&1 || true
    endscript
}
EOF

# Create log directory
sudo mkdir -p /var/log/rag-app
sudo chown ubuntu:ubuntu /var/log/rag-app

echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Update /opt/rag-app/backend/.env with your Pinecone credentials"
echo "2. Restart the backend: sudo systemctl restart rag-backend"
echo "3. Check status: /opt/rag-app/monitor.sh"
echo "4. Access the application at: http://<your-ec2-public-ip>"
echo ""
echo "Useful commands:"
echo "- Check logs: sudo journalctl -u rag-backend -f"
echo "- Restart backend: sudo systemctl restart rag-backend"
echo "- Monitor status: /opt/rag-app/monitor.sh"
echo "- Update app: /opt/rag-app/update.sh"
