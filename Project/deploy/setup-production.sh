#!/bin/bash

# Petrol Station Management System - Production Setup Script
# This script sets up the application on Hostinger VPS for production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="petrol-station"
APP_DIR="/opt/$APP_NAME"
USER_NAME="petrol-user"
DOMAIN_NAME="your-domain.com"

echo -e "${BLUE}🚀 Starting Petrol Station Management System Production Setup${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}"
   exit 1
fi

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Install required packages
echo -e "${YELLOW}📦 Installing required packages...${NC}"
apt install -y python3 python3-pip python3-venv nginx mysql-server ufw certbot python3-certbot-nginx

# Create application user
echo -e "${YELLOW}👤 Creating application user...${NC}"
if ! id "$USER_NAME" &>/dev/null; then
    useradd -m -s /bin/bash $USER_NAME
    echo -e "${GREEN}✅ Created user: $USER_NAME${NC}"
else
    echo -e "${BLUE}ℹ️  User $USER_NAME already exists${NC}"
fi

# Create application directory
echo -e "${YELLOW}📁 Creating application directory...${NC}"
mkdir -p $APP_DIR
mkdir -p /var/log/$APP_NAME
mkdir -p /var/backups/$APP_NAME
chown -R $USER_NAME:$USER_NAME $APP_DIR
chown -R $USER_NAME:$USER_NAME /var/log/$APP_NAME
chown -R $USER_NAME:$USER_NAME /var/backups/$APP_NAME

# Setup MySQL database
echo -e "${YELLOW}🗄️  Setting up MySQL database...${NC}"
mysql -e "CREATE DATABASE IF NOT EXISTS Petrolpump_Management_Enhanced CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS 'petrol_user'@'localhost' IDENTIFIED BY 'CHANGE_THIS_PASSWORD';"
mysql -e "GRANT ALL PRIVILEGES ON Petrolpump_Management_Enhanced.* TO 'petrol_user'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

echo -e "${RED}⚠️  IMPORTANT: Please change the MySQL password in the .env file and update the GRANT statement above!${NC}"

# Setup firewall
echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force reload

# Install SSL certificate (optional - requires domain)
read -p "Do you want to setup SSL certificate now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🔒 Setting up SSL certificate...${NC}"
    certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME
fi

echo -e "${GREEN}✅ Production environment setup completed!${NC}"
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Copy your application files to $APP_DIR"
echo "2. Update the .env file with production settings"
echo "3. Run the deployment script: ./deploy-production.sh"
echo "4. Start the application service"
echo ""
echo -e "${YELLOW}⚠️  Remember to:${NC}"
echo "- Change the MySQL password in the .env file"
echo "- Update API keys for production"
echo "- Configure backup settings"
echo "- Test the application thoroughly"
