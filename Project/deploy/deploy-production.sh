#!/bin/bash

# Petrol Station Management System - Production Deployment Script
# Run this script after setup-production.sh and after copying application files

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

echo -e "${BLUE}🚀 Starting Petrol Station Management System Production Deployment${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}"
   exit 1
fi

# Check if application directory exists
if [[ ! -d "$APP_DIR" ]]; then
    echo -e "${RED}❌ Application directory $APP_DIR does not exist. Please run setup-production.sh first.${NC}"
    exit 1
fi

# Install Python dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
cd $APP_DIR
sudo -u $USER_NAME python3 -m venv venv
sudo -u $USER_NAME bash -c "source venv/bin/activate && pip install --upgrade pip"
sudo -u $USER_NAME bash -c "source venv/bin/activate && pip install -r deploy/requirements-production.txt"

# Setup environment file
echo -e "${YELLOW}⚙️  Setting up environment configuration...${NC}"
if [[ ! -f ".env" ]]; then
    cp deploy/.env.production .env
    echo -e "${RED}⚠️  IMPORTANT: Please edit .env file with your production settings!${NC}"
    echo -e "${YELLOW}   - Update database password${NC}"
    echo -e "${YELLOW}   - Set secure SECRET_KEY${NC}"
    echo -e "${YELLOW}   - Configure API keys${NC}"
fi

# Create database tables
echo -e "${YELLOW}🗄️  Creating database tables...${NC}"
sudo -u $USER_NAME bash -c "source venv/bin/activate && python create_enhanced_db_complete.py"

# Setup systemd service
echo -e "${YELLOW}🔧 Setting up systemd service...${NC}"
cp deploy/petrol-station.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable $APP_NAME

# Setup nginx
echo -e "${YELLOW}🌐 Setting up nginx configuration...${NC}"
cp deploy/nginx.conf /etc/nginx/sites-available/$APP_NAME
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# Setup log rotation
echo -e "${YELLOW}📝 Setting up log rotation...${NC}"
cat > /etc/logrotate.d/$APP_NAME << EOF
/var/log/$APP_NAME/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER_NAME $USER_NAME
    postrotate
        systemctl reload $APP_NAME
    endscript
}
EOF

# Setup backup script
echo -e "${YELLOW}💾 Setting up backup script...${NC}"
cat > /usr/local/bin/backup-$APP_NAME.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/petrol-station"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

mkdir -p $BACKUP_DIR
mysqldump -u petrol_user -p'YOUR_DB_PASSWORD' Petrolpump_Management_Enhanced > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
EOF

chmod +x /usr/local/bin/backup-$APP_NAME.sh

# Setup backup cron job
echo -e "${YELLOW}⏰ Setting up backup cron job...${NC}"
echo "0 2 * * * root /usr/local/bin/backup-petrol-station.sh" > /etc/cron.d/$APP_NAME-backup

# Set proper permissions
echo -e "${YELLOW}🔒 Setting proper permissions...${NC}"
chown -R $USER_NAME:$USER_NAME $APP_DIR
chmod 755 $APP_DIR
chmod 644 $APP_DIR/.env

# Start the application
echo -e "${YELLOW}▶️  Starting the application...${NC}"
systemctl start $APP_NAME

# Wait a moment and check status
sleep 5
if systemctl is-active --quiet $APP_NAME; then
    echo -e "${GREEN}✅ Application started successfully!${NC}"
else
    echo -e "${RED}❌ Failed to start application. Check logs with: journalctl -u $APP_NAME${NC}"
    exit 1
fi

# Final status
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Service Status:${NC}"
systemctl status $APP_NAME --no-pager -l
echo ""
echo -e "${BLUE}🌐 Application should be available at:${NC}"
echo "  HTTP:  http://your-domain.com"
echo "  HTTPS: https://your-domain.com"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "  Start:   systemctl start $APP_NAME"
echo "  Stop:    systemctl stop $APP_NAME"
echo "  Restart: systemctl restart $APP_NAME"
echo "  Logs:    journalctl -u $APP_NAME -f"
echo "  Backup:  /usr/local/bin/backup-$APP_NAME.sh"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "- Update your .env file with production credentials"
echo "- Configure SSL certificate if not done already"
echo "- Test all application features"
echo "- Monitor logs regularly"
