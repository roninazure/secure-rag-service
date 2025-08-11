# 🚀 Private GPT AWS EC2 Deployment Guide

## Overview
This guide walks you through deploying your Private GPT system from your laptop to an AWS EC2 t3.micro instance.

## Prerequisites

### 1. AWS Account Setup
- [ ] AWS account with billing configured
- [ ] IAM user with programmatic access for Bedrock
- [ ] AWS CLI configured locally (optional but helpful)

### 2. Required Credentials
Gather these before starting:
- **AWS Access Key ID** (for Bedrock)
- **AWS Secret Access Key** (for Bedrock)
- **Pinecone API Key** (from your Pinecone dashboard)
- **Pinecone Index Name** (should be `privategpt-index`)

## 📋 Deployment Steps

### Step 1: Launch EC2 Instance

1. **Go to EC2 Console** → Launch Instance
2. **Configure Instance:**
   ```
   Name: PrivateGPT-Pilot
   AMI: Ubuntu Server 22.04 LTS (64-bit x86)
   Instance Type: t3.micro
   Key Pair: Create new or use existing (save .pem file!)
   ```

3. **Network Settings:**
   - VPC: Default
   - Subnet: No preference
   - Auto-assign Public IP: Enable
   
4. **Configure Security Group:**
   ```
   Name: privategpt-sg
   Rules:
   - SSH (22): Your IP only
   - HTTP (80): Anywhere (0.0.0.0/0)
   - HTTPS (443): Anywhere (0.0.0.0/0)
   - Custom TCP (8000): Your IP only (for testing)
   ```

5. **Storage:**
   - 20 GB gp3 (or larger if needed)

6. **Launch Instance** and wait for it to initialize

### Step 2: Connect to Your Instance

```bash
# Set correct permissions on your key
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 3: Upload Your Code

From your **local machine**, upload your code:

```bash
# Create a tarball of your project
cd ~/privategpt-ui
tar -czf privategpt.tar.gz --exclude=node_modules --exclude=venv --exclude=.env .

# Upload to EC2
scp -i your-key.pem privategpt.tar.gz ubuntu@YOUR_EC2_PUBLIC_IP:~/

# On the EC2 instance, extract it
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
mkdir -p privategpt-ui
tar -xzf privategpt.tar.gz -C privategpt-ui/
```

### Step 4: Run the Deployment Script

On the EC2 instance:

```bash
# Make the script executable
chmod +x ~/privategpt-ui/deploy_to_aws.sh

# Run the deployment script
cd ~
./privategpt-ui/deploy_to_aws.sh
```

This will take about 10-15 minutes and will:
- Install all system dependencies
- Setup Python 3.11 and Node.js
- Configure Nginx as reverse proxy
- Create systemd service for backend
- Setup monitoring scripts

### Step 5: Configure Environment Variables

```bash
# Copy the template
cp ~/privategpt-ui/backend/.env.template ~/privategpt-ui/backend/.env

# Edit with your credentials
nano ~/privategpt-ui/backend/.env
```

Add your actual credentials:
```env
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=YYYYYYYYYYYYYYYYYYYYYYYY
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.titan-text-express-v1
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
PINECONE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PINECONE_INDEX_NAME=privategpt-index
PINECONE_ENVIRONMENT=us-east-1
```

Save and exit (Ctrl+X, Y, Enter)

### Step 6: Start the Backend Service

```bash
# Start the service
sudo systemctl start privategpt-backend

# Check if it's running
sudo systemctl status privategpt-backend

# View logs if needed
sudo journalctl -u privategpt-backend -f
```

### Step 7: Test Your Deployment

1. **Check system status:**
   ```bash
   ./check_privategpt.sh
   ```

2. **Test the API directly:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Access from browser:**
   ```
   http://YOUR_EC2_PUBLIC_IP
   ```

### Step 8: Ingest Your Documents

```bash
# Run the document ingestion script
cd ~/privategpt-ui/backend
source venv/bin/activate
python ingest_clean_documents.py
```

## 🔍 Monitoring & Maintenance

### View Logs
```bash
# Backend logs
sudo journalctl -u privategpt-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Application logs
tail -f /var/log/privategpt/backend.log
```

### Restart Services
```bash
# Restart backend
sudo systemctl restart privategpt-backend

# Restart Nginx
sudo systemctl restart nginx
```

### Update Code
```bash
cd ~/privategpt-ui
git pull
npm --prefix frontend install
npm --prefix frontend run build
sudo systemctl restart privategpt-backend
```

## 🛡️ Security Considerations

### For Pilot Phase
1. **Restrict access** - Update security group to limit access to pilot users' IPs
2. **Monitor usage** - Check logs regularly for unusual activity
3. **Backup regularly** - Create EBS snapshots before major changes

### Before Production
1. **Enable HTTPS** - Setup SSL certificate with Let's Encrypt
2. **Add authentication** - Implement API key or OAuth
3. **Use IAM roles** - Replace .env credentials with instance IAM role
4. **Enable CloudWatch** - Setup monitoring and alerts
5. **Add rate limiting** - Prevent abuse

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check logs
sudo journalctl -u privategpt-backend -n 50

# Common issues:
# - Missing .env file
# - Wrong Python path
# - Port 8000 already in use
```

### Frontend not loading
```bash
# Check Nginx config
sudo nginx -t
sudo systemctl status nginx

# Verify frontend build exists
ls -la ~/privategpt-ui/frontend/dist/
```

### Can't connect to Bedrock
```bash
# Test AWS credentials
cd ~/privategpt-ui/backend
source venv/bin/activate
python -c "import boto3; print(boto3.client('bedrock-runtime').list_foundation_models())"
```

### Memory issues (t3.micro has only 1GB RAM)
```bash
# Check memory usage
free -h

# If needed, add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 📊 Performance Optimization

For t3.micro (limited resources):

1. **Reduce workers:**
   ```bash
   # Edit service file
   sudo nano /etc/systemd/system/privategpt-backend.service
   # Change --workers 2 to --workers 1
   sudo systemctl daemon-reload
   sudo systemctl restart privategpt-backend
   ```

2. **Enable response caching** (future enhancement)

3. **Monitor CPU credits:**
   ```bash
   # Install CloudWatch agent for detailed metrics
   ```

## ✅ Success Checklist

- [ ] EC2 instance running
- [ ] Security group configured correctly
- [ ] Code deployed and extracted
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Backend service running
- [ ] Nginx serving frontend
- [ ] Can access UI via browser
- [ ] Chat functionality working
- [ ] Documents ingested to Pinecone

## 🎯 Next Steps

Once deployed and tested:

1. **Share with pilot users:**
   - Provide the EC2 public IP
   - Create user guide
   - Setup feedback collection

2. **Monitor pilot phase:**
   - Track usage patterns
   - Collect performance metrics
   - Gather user feedback

3. **Plan for production:**
   - Estimate resource needs
   - Design scalable architecture
   - Plan security enhancements

---

**Support:** If you encounter issues, check the logs first, then refer to the troubleshooting section above.
