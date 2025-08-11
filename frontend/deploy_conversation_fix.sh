#!/bin/bash

# Deploy conversation history fix to EC2

EC2_IP="44.202.131.48"
KEY_PATH="$HOME/.ssh/Scott-Key.pem"

echo "Deploying conversation history fix to EC2..."

# Copy the updated chat.py file
scp -i "$KEY_PATH" \
    /Users/scottsteele/privategpt-ui/backend/app/api/chat.py \
    ec2-user@$EC2_IP:/home/ec2-user/privategpt/backend/app/api/

# Restart the backend service on EC2
ssh -i "$KEY_PATH" ec2-user@$EC2_IP << 'EOF'
    echo "Restarting backend service..."
    sudo systemctl restart privategpt-backend
    sleep 3
    
    # Check if service is running
    if sudo systemctl is-active --quiet privategpt-backend; then
        echo "✅ Backend service restarted successfully"
        echo "Checking latest logs..."
        sudo journalctl -u privategpt-backend -n 20 --no-pager
    else
        echo "❌ Backend service failed to start"
        sudo journalctl -u privategpt-backend -n 50 --no-pager
    fi
EOF

echo ""
echo "Deployment complete!"
echo "Test the conversation continuity at: https://$EC2_IP"
echo ""
echo "Test sequence:"
echo "1. Ask: 'What are the types available'"
echo "2. After response, say: 'Criminal please'"
echo "3. The bot should now provide criminal-specific information"
