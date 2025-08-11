#!/bin/bash

# AWS EC2 IP Management Script
# Helps manage dynamic IP addresses for your EC2 instance

CONFIG_FILE="$HOME/.privategpt_ec2_config"
SSH_KEY="$HOME/.ssh/Scott-Key.pem"
SSH_USER="ec2-user"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to save IP
save_ip() {
    local ip=$1
    echo "EC2_HOST=$ip" > "$CONFIG_FILE"
    echo "LAST_UPDATED=$(date '+%Y-%m-%d %H:%M:%S')" >> "$CONFIG_FILE"
    echo -e "${GREEN}✓ IP address saved: $ip${NC}"
}

# Function to load saved IP
load_ip() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
        echo -e "${BLUE}Last saved IP: $EC2_HOST${NC}"
        echo "Last updated: $LAST_UPDATED"
        return 0
    else
        echo "No saved IP address found."
        return 1
    fi
}

# Main menu
echo "==========================================="
echo "Private GPT EC2 IP Manager"
echo "==========================================="
echo ""

# Check if we have a saved IP
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    echo "Last known IP: $EC2_HOST"
    echo "Last updated: $LAST_UPDATED"
    echo ""
    echo "Options:"
    echo "1) Use saved IP ($EC2_HOST)"
    echo "2) Enter new IP"
    echo "3) Get IP from AWS CLI (requires configured AWS CLI)"
    read -p "Choice [1-3]: " choice
else
    echo "No saved IP found."
    echo ""
    echo "Options:"
    echo "2) Enter new IP manually"
    echo "3) Get IP from AWS CLI (requires configured AWS CLI)"
    read -p "Choice [2-3]: " choice
fi

case $choice in
    1)
        if [ -z "$EC2_HOST" ]; then
            echo "No saved IP available. Please enter IP manually."
            read -p "IP Address: " EC2_HOST
        fi
        ;;
    2)
        read -p "Enter new IP address: " EC2_HOST
        ;;
    3)
        echo "Attempting to get IP from AWS CLI..."
        echo "Enter your instance ID:"
        read -p "Instance ID: " INSTANCE_ID
        EC2_HOST=$(aws ec2 describe-instances \
            --instance-ids "$INSTANCE_ID" \
            --query 'Reservations[0].Instances[0].PublicIpAddress' \
            --output text 2>/dev/null)
        
        if [ "$EC2_HOST" = "None" ] || [ -z "$EC2_HOST" ]; then
            echo "Could not retrieve IP. Is the instance running?"
            exit 1
        fi
        echo -e "${GREEN}Retrieved IP: $EC2_HOST${NC}"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Validate IP format
if [[ ! $EC2_HOST =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    echo "Invalid IP address format: $EC2_HOST"
    exit 1
fi

# Save the IP for next time
save_ip "$EC2_HOST"

echo ""
echo "Testing connection to $EC2_HOST..."
if ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$SSH_USER@$EC2_HOST" "echo 'Connected successfully'" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Connection successful!${NC}"
    echo ""
    echo "What would you like to do?"
    echo "1) Run startup check"
    echo "2) Run auto-recovery"
    echo "3) SSH into instance"
    echo "4) Open web interface in browser"
    echo "5) Exit"
    read -p "Choice [1-5]: " action
    
    case $action in
        1)
            echo "$EC2_HOST" | ./aws_startup_check.sh
            ;;
        2)
            echo "$EC2_HOST" | ./aws_auto_recovery.sh
            ;;
        3)
            ssh -i "$SSH_KEY" "$SSH_USER@$EC2_HOST"
            ;;
        4)
            echo "Opening https://$EC2_HOST/ in your default browser..."
            echo "(You'll need to accept the self-signed certificate warning)"
            open "https://$EC2_HOST/" 2>/dev/null || xdg-open "https://$EC2_HOST/" 2>/dev/null || echo "Please open manually: https://$EC2_HOST/"
            ;;
        5)
            exit 0
            ;;
        *)
            echo "Invalid choice"
            ;;
    esac
else
    echo -e "${YELLOW}⚠ Cannot connect to $EC2_HOST${NC}"
    echo ""
    echo "Please check:"
    echo "1. Instance is running in AWS Console"
    echo "2. Security group allows SSH (port 22) from your IP"
    echo "3. The IP address is correct"
fi
