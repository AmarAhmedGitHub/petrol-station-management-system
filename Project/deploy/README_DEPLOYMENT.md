# 🚀 Petrol Station Management System - Hostinger VPS Deployment Guide

## 📋 Overview

This guide provides step-by-step instructions for deploying the Petrol Station Management System to a Hostinger VPS server for production use.

## 🔧 Prerequisites

- Hostinger VPS with Ubuntu/Debian
- Domain name pointed to your VPS IP
- SSH access to the server
- Basic Linux command knowledge

## 📁 Deployment Files

The `deploy/` directory contains all necessary files for production deployment:

- `requirements-production.txt` - Python dependencies for production
- `.env.production` - Production environment configuration template
- `nginx.conf` - Nginx web server configuration
- `petrol-station.service` - Systemd service configuration
- `setup-production.sh` - Initial server setup script
- `deploy-production.sh` - Application deployment script

## 🚀 Deployment Steps

### Step 1: Prepare Your Local Files

1. Copy the entire project to your local machine
2. Update the `.env.production` file with your production settings:
   ```bash
   # Update these values:
   DB_PASSWORD=your_secure_mysql_password
   SECRET_KEY=your_very_secure_random_key_here
   PTS2_API_KEY=your_pts2_production_key
   ATG_API_KEY=your_atg_production_key
   ```

### Step 2: Server Setup

1. Connect to your VPS via SSH:
   ```bash
   ssh root@your-vps-ip
   ```

2. Run the setup script:
   ```bash
   wget https://raw.githubusercontent.com/your-repo/setup-production.sh
   chmod +x setup-production.sh
   ./setup-production.sh
   ```

3. The script will:
   - Update system packages
   - Install required software (Python, MySQL, Nginx)
   - Create application user and directories
   - Setup basic firewall rules
   - Configure MySQL database

### Step 3: Upload Application Files

Upload your application files to the VPS:

```bash
# Using SCP from your local machine
scp -r /path/to/your/project root@your-vps-ip:/opt/petrol-station/

# Or using rsync for better performance
rsync -avz /path/to/your/project root@your-vps-ip:/opt/petrol-station/
```

### Step 4: Deploy Application

On the VPS, run the deployment script:

```bash
cd /opt/petrol-station
chmod +x deploy/deploy-production.sh
./deploy/deploy-production.sh
```

The deployment script will:
- Create Python virtual environment
- Install dependencies
- Setup environment configuration
- Create database tables
- Configure systemd service
- Setup nginx reverse proxy
- Configure log rotation
- Setup automated backups

### Step 5: SSL Certificate Setup

Setup SSL certificate for HTTPS:

```bash
# Install certbot if not already installed
apt install certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d your-domain.com -d www.your-domain.com

# Test renewal
certbot renew --dry-run
```

### Step 6: Final Configuration

1. Edit the `.env` file with production values:
   ```bash
   nano /opt/petrol-station/.env
   ```

2. Update nginx configuration with your domain:
   ```bash
   nano /etc/nginx/sites-available/petrol-station
   # Replace 'your-domain.com' with your actual domain
   ```

3. Restart services:
   ```bash
   systemctl reload nginx
   systemctl restart petrol-station
   ```

## 🔍 Testing Deployment

### Health Checks

1. Check application status:
   ```bash
   systemctl status petrol-station
   ```

2. Check nginx status:
   ```bash
   systemctl status nginx
   ```

3. View application logs:
   ```bash
   journalctl -u petrol-station -f
   ```

4. Test web access:
   ```bash
   curl -I https://your-domain.com/health
   ```

### Application Testing

1. Access the application at `https://your-domain.com`
2. Test login functionality
3. Verify database connections
4. Test sensor integrations (if applicable)

## 🔧 Management Commands

### Application Management
```bash
# Start application
systemctl start petrol-station

# Stop application
systemctl stop petrol-station

# Restart application
systemctl restart petrol-station

# Check status
systemctl status petrol-station
```

### Log Management
```bash
# View application logs
journalctl -u petrol-station -f

# View nginx logs
tail -f /var/log/nginx/petrol-station.access.log
tail -f /var/log/nginx/petrol-station.error.log
```

### Backup Management
```bash
# Manual backup
/usr/local/bin/backup-petrol-station.sh

# List backups
ls -la /var/backups/petrol-station/
```

## 🔒 Security Considerations

1. **Change default passwords** in the `.env` file
2. **Use strong SECRET_KEY** for session encryption
3. **Configure firewall** properly (UFW is pre-configured)
4. **Keep system updated** with regular security patches
5. **Monitor logs** for suspicious activity
6. **Use HTTPS only** (HTTP redirects to HTTPS)

## 📊 Monitoring

### System Monitoring
```bash
# Check system resources
htop
df -h
free -h

# Check application performance
systemctl status petrol-station
journalctl -u petrol-station --since "1 hour ago"
```

### Automated Monitoring
The deployment includes:
- Daily database backups
- Log rotation
- Service monitoring via systemd
- Nginx access/error logs

## 🆘 Troubleshooting

### Common Issues

1. **Application won't start**:
   ```bash
   journalctl -u petrol-station -n 50
   ```

2. **Database connection errors**:
   - Check MySQL service: `systemctl status mysql`
   - Verify credentials in `.env`
   - Test connection: `mysql -u petrol_user -p Petrolpump_Management_Enhanced`

3. **Nginx errors**:
   ```bash
   nginx -t
   systemctl status nginx
   tail -f /var/log/nginx/error.log
   ```

4. **Permission errors**:
   ```bash
   chown -R petrol-user:petrol-user /opt/petrol-station
   chmod 644 /opt/petrol-station/.env
   ```

### Performance Optimization

1. **Database optimization**:
   ```bash
   mysql -u root -p Petrolpump_Management_Enhanced < optimize_db.sql
   ```

2. **Memory limits**: Adjust in `petrol-station.service`
3. **Backup scheduling**: Modify `/etc/cron.d/petrol-station-backup`

## 📞 Support

For issues or questions:
1. Check application logs
2. Review nginx error logs
3. Verify configuration files
4. Test database connectivity
5. Check system resources

## 🔄 Updates

To update the application:
1. Upload new files to `/opt/petrol-station`
2. Restart the service: `systemctl restart petrol-station`
3. Monitor logs for any issues

---

**Deployment completed successfully! 🎉**

Your Petrol Station Management System is now running in production on Hostinger VPS.
