# Private GPT AWS EC2 - Quick Reference

## 🚀 Essential Commands

### SSH Access
```bash
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP
```

### Service Management
```bash
# Start/Stop/Restart Backend
sudo systemctl start privategpt-backend
sudo systemctl stop privategpt-backend
sudo systemctl restart privategpt-backend
sudo systemctl status privategpt-backend

# View Logs
sudo journalctl -u privategpt-backend -f    # Live logs
sudo journalctl -u privategpt-backend -n 100 # Last 100 lines
```

### Quick Health Check
```bash
# Run monitoring script
./check_privategpt.sh

# Test API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "session_id": "test"}'
```

### Update Environment Variables
```bash
nano ~/privategpt-ui/backend/.env
sudo systemctl restart privategpt-backend
```

## 📁 Important File Locations

```
/home/ubuntu/privategpt-ui/          # Main application directory
├── backend/                         # FastAPI backend
│   ├── .env                        # Environment variables
│   ├── main.py                     # Main application
│   └── venv/                       # Python virtual environment
├── frontend/                        # React frontend
│   └── dist/                       # Built static files
└── deploy_to_aws.sh                # Deployment script

/etc/nginx/sites-available/privategpt    # Nginx config
/etc/systemd/system/privategpt-backend.service  # Systemd service
/var/log/privategpt/                 # Application logs
```

## 🔧 Common Fixes

### Out of Memory
```bash
# Check memory
free -h

# Add swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Reduce workers to 1
sudo nano /etc/systemd/system/privategpt-backend.service
# Change: --workers 2 → --workers 1
sudo systemctl daemon-reload
sudo systemctl restart privategpt-backend
```

### Backend Won't Start
```bash
# Check for errors
sudo journalctl -u privategpt-backend -n 50

# Common fixes:
# 1. Check .env file exists and has correct values
ls -la ~/privategpt-ui/backend/.env

# 2. Verify Python environment
source ~/privategpt-ui/backend/venv/bin/activate
python --version  # Should be 3.11

# 3. Check port 8000
sudo lsof -i :8000
```

### Frontend Issues
```bash
# Rebuild frontend
cd ~/privategpt-ui/frontend
npm install
npm run build

# Check Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### Bedrock Connection Issues
```bash
# Test AWS credentials
cd ~/privategpt-ui/backend
source venv/bin/activate
python -c "
import boto3
client = boto3.client('bedrock-runtime', region_name='us-east-1')
print('Connection successful')
"
```

## 📊 Performance Monitoring

```bash
# CPU and Memory
htop  # Install with: sudo apt install htop

# Disk usage
df -h

# Network connections
sudo netstat -tulpn | grep LISTEN

# Process info
ps aux | grep python
ps aux | grep nginx
```

## 🔄 Update Deployment

```bash
# Pull latest code (if using git)
cd ~/privategpt-ui
git pull

# Rebuild frontend
cd frontend
npm install
npm run build

# Update backend dependencies
cd ../backend
source venv/bin/activate
pip install -r requirements.txt

# Restart services
sudo systemctl restart privategpt-backend
sudo systemctl restart nginx
```

## 🛑 Emergency Shutdown

```bash
# Stop all services
sudo systemctl stop privategpt-backend
sudo systemctl stop nginx

# Disable auto-start
sudo systemctl disable privategpt-backend
```

## 📝 Useful AWS CLI Commands

```bash
# Get instance metadata (from within EC2)
curl http://169.254.169.254/latest/meta-data/instance-id
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Create EBS snapshot (backup)
aws ec2 create-snapshot --volume-id vol-xxxxx --description "PrivateGPT backup"

# Check CPU credits (t3.micro)
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUCreditBalance \
  --dimensions Name=InstanceId,Value=i-xxxxx \
  --statistics Average \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600
```

## 🔑 Security Group Rules

```bash
# View current rules (from local machine)
aws ec2 describe-security-groups --group-ids sg-xxxxx

# Add IP to whitelist
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 80 \
  --cidr YOUR_IP/32
```

## 📞 Support Checklist

Before asking for help, check:
1. ✓ Service status: `sudo systemctl status privategpt-backend`
2. ✓ Logs: `sudo journalctl -u privategpt-backend -n 50`
3. ✓ Environment vars: `cat ~/privategpt-ui/backend/.env`
4. ✓ Memory: `free -h`
5. ✓ Disk space: `df -h`
6. ✓ Network: `curl http://localhost:8000/health`

---
**EC2 Instance:** t3.micro (1 GB RAM, 2 vCPU)  
**Region:** us-east-1  
**Stack:** Ubuntu 22.04, Python 3.11, Node.js 18, Nginx  
**Models:** AWS Bedrock Titan (Text Express & Embed v2)
