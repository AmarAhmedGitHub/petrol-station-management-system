#!/bin/bash

# Final Deployment Script for Hostinger VPS
# Run this on your Hostinger VPS after uploading all files

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Final Petrol Station Management System Deployment${NC}"

# Check if running on Hostinger VPS
if ! curl -s http://169.254.169.254/latest/meta-data/ &>/dev/null && ! hostname | grep -i hostinger &>/dev/null; then
    echo -e "${YELLOW}⚠️  Warning: Not detected as Hostinger VPS. Continuing anyway...${NC}"
fi

# Update system
echo -e "${YELLOW}📦 Updating system...${NC}"
apt update && apt upgrade -y

# Install Docker and Docker Compose
echo -e "${YELLOW}🐳 Installing Docker...${NC}"
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
echo -e "${YELLOW}🐳 Installing Docker Compose...${NC}"
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Enable and start Docker
systemctl enable docker
systemctl start docker

# Create deployment directory
mkdir -p /opt/petrol-station
cd /opt/petrol-station

# Copy deployment files (assuming they're uploaded)
cp -r /path/to/uploaded/Project/* . 2>/dev/null || echo "Files already in place"

# Make scripts executable
chmod +x deploy/*.sh

# Setup environment
if [[ ! -f ".env" ]]; then
    cp deploy/.env.production .env
    echo -e "${RED}⚠️  CRITICAL: Edit .env file with your actual credentials!${NC}"
    echo -e "${YELLOW}  Required changes:${NC}"
    echo "  - DB_PASSWORD"
    echo "  - SECRET_KEY"
    echo "  - PTS2_API_KEY"
    echo "  - ATG_API_KEY"
    echo "  - Domain name in nginx.conf"
    read -p "Press Enter after editing .env file..."
fi

# Run Docker deployment
echo -e "${YELLOW}🐳 Starting Docker deployment...${NC}"
cd deploy
./docker-deploy.sh

# Setup domain and SSL
echo -e "${YELLOW}🔒 Setting up SSL certificate...${NC}"
read -p "Enter your domain name: " DOMAIN

# Update nginx configuration
sed -i "s/your-domain.com/$DOMAIN/g" nginx.conf

# Reload nginx
docker-compose exec petrol-station-nginx nginx -s reload

# Install certbot for SSL
apt install -y certbot

# Get SSL certificate
certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --agree-tos --email admin@$DOMAIN --non-interactive

# Update nginx for SSL
cat > nginx.conf << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://petrol-station-app:8501;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering off;
    }
}
EOF

# Reload services
docker-compose down
docker-compose up -d

# Setup automatic SSL renewal
echo "0 12 * * * root certbot renew --quiet && docker-compose exec petrol-station-nginx nginx -s reload" > /etc/cron.d/certbot-renewal

# Final status
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}🌐 Your application is now live at:${NC}"
echo "  HTTPS: https://$DOMAIN"
echo "  HTTP:  http://$DOMAIN (redirects to HTTPS)"
echo ""
echo -e "${BLUE}🔧 Management commands:${NC}"
echo "  cd /opt/petrol-station/deploy"
echo "  docker-compose logs -f          # View logs"
echo "  docker-compose restart          # Restart services"
echo "  docker-compose down             # Stop all services"
echo "  docker-compose up -d            # Start all services"
echo ""
echo -e "${BLUE}📊 Monitoring:${NC}"
echo "  docker-compose ps               # Check service status"
echo "  docker stats                    # Resource usage"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "- Test all application features"
echo "- Monitor logs regularly"
echo "- Keep system updated"
echo "- Backup data regularly"
