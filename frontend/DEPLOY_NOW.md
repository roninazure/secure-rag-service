# 🚀 EC2 Deployment Instructions - RAG System

## Prerequisites Checklist
✅ EC2 Instance: i-0fadb55d0e66b42f0 (t2.micro)  
✅ IAM Role: EC2-Bedrock-Role (attached)  
✅ Key Pair: Scott-Key.pem  
✅ Deployment Package: rag-deployment-new.tar.gz (21MB)  
✅ Setup Script: ec2-setup.sh  

## Step 1: Start Your EC2 Instance

1. **Go to AWS Console** → EC2 → Instances
2. **Select** your instance `i-0fadb55d0e66b42f0`
3. **Click** "Instance State" → "Start Instance"
4. **Wait** for State to show "Running" (about 1 minute)
5. **Copy** the assigned **Public IPv4 address**

## Step 2: Update Security Group

Make sure your instance's security group allows:
- **SSH (22)** - from your IP
- **HTTP (80)** - from anywhere (0.0.0.0/0)
- **Custom TCP (8000)** - from your IP (for testing)

## Step 3: Connect to Your EC2 Instance

```bash
# Make sure your key has correct permissions
chmod 400 /path/to/Scott-Key.pem

# Connect to EC2 (replace XX.XX.XX.XX with your public IP)
ssh -i /path/to/Scott-Key.pem ubuntu@XX.XX.XX.XX
```

## Step 4: Upload Files to EC2

Open a **new terminal** on your Mac and run:

```bash
# Set your EC2 IP
export EC2_IP="XX.XX.XX.XX"  # Replace with your EC2 public IP
export KEY_PATH="/path/to/Scott-Key.pem"  # Replace with your key path

# Upload deployment package
scp -i $KEY_PATH /Users/scottsteele/privategpt-ui/rag-deployment-new.tar.gz ubuntu@$EC2_IP:~/

# Upload setup script
scp -i $KEY_PATH /Users/scottsteele/privategpt-ui/ec2-setup.sh ubuntu@$EC2_IP:~/
```

## Step 5: Run Setup Script

Back in your **SSH session**:

```bash
# Make script executable
chmod +x ~/ec2-setup.sh

# Run the setup (will take 5-10 minutes)
./ec2-setup.sh
```

## Step 6: Configure Pinecone Credentials

```bash
# Edit the environment file
sudo nano /opt/rag-app/backend/.env
```

Update these values with your actual credentials:
```
PINECONE_API_KEY=pcsk_5t1Rrk_EF23ppxsHtvGzSjMWchtFmdysfFs7tXrhkdiGw6oF9b1jQJHpQgKxGwgJUj5BbD
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=privategpt-embeddings
```

Save and exit (Ctrl+X, Y, Enter)

## Step 7: Restart Backend Service

```bash
# Restart with new credentials
sudo systemctl restart rag-backend

# Check if running
sudo systemctl status rag-backend

# View logs if needed
sudo journalctl -u rag-backend -f
```

## Step 8: Test Your Deployment

1. **Test Backend Health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test from Browser**:
   - Open `http://YOUR-EC2-PUBLIC-IP` in your browser
   - You should see the chat interface!

3. **Test Chat**:
   - Try asking: "What are the billing rates?"
   - Or: "What is the firm's HR policy?"

## Step 9: Monitor Your System

```bash
# Run monitoring script
/opt/rag-app/monitor.sh

# Check real-time logs
sudo journalctl -u rag-backend -f

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
```

## Troubleshooting

### If backend won't start:
```bash
# Check logs
sudo journalctl -u rag-backend -n 50

# Test Python directly
cd /opt/rag-app/backend
source ../venv/bin/activate
python -c "from main import app; print('Import successful')"
```

### If frontend shows connection errors:
```bash
# Check Nginx config
sudo nginx -t
sudo systemctl restart nginx

# Test API directly
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

### If IAM role issues:
```bash
# Test AWS credentials
aws sts get-caller-identity
aws bedrock list-foundation-models --region us-east-1
```

## Security Notes

⚠️ **Important**: Your EC2 instance is using an IAM role for AWS access, which is more secure than hardcoding credentials.

For production:
1. Set up HTTPS with Let's Encrypt
2. Restrict security group rules
3. Enable CloudWatch monitoring
4. Set up regular backups

## Quick Commands Reference

```bash
# Service Management
sudo systemctl start rag-backend
sudo systemctl stop rag-backend
sudo systemctl restart rag-backend
sudo systemctl status rag-backend

# Logs
sudo journalctl -u rag-backend -f  # Follow backend logs
sudo tail -f /var/log/nginx/error.log  # Nginx errors

# Updates
cd /opt/rag-app
./update.sh  # Run update script

# Monitoring
./monitor.sh  # Check system status
```

## Success Checklist

When everything is working:
- [ ] EC2 instance is running
- [ ] Can SSH into instance
- [ ] Backend service is active
- [ ] Nginx is serving frontend
- [ ] Can access chat UI in browser
- [ ] Chat responses work correctly
- [ ] No errors in logs

---

## Need Help?

If you encounter issues:
1. Check the logs first
2. Verify all services are running
3. Test each component individually
4. Check security group rules
5. Verify IAM role permissions

Your system should be accessible at:
**http://YOUR-EC2-PUBLIC-IP**

Good luck with your pilot deployment! 🎉
