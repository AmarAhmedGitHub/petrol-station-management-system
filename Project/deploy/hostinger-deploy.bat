@echo off
REM Petrol Station Management System - Hostinger Deployment Script (Windows)
REM Run this script locally to deploy to Hostinger VPS

echo 🚀 Starting Hostinger VPS Deployment...

REM Configuration - Update these values
set VPS_HOST=your-vps-ip
set VPS_USER=root
set DOMAIN=your-domain.com
set DB_PASSWORD=your_secure_db_password
set SECRET_KEY=your_very_secure_random_key_here

echo 📦 Preparing deployment files...

REM Create deployment package
if not exist deploy (
    echo ❌ Deploy directory not found!
    pause
    exit /b 1
)

REM Copy files to deployment directory
xcopy /E /I /Y Project deploy\temp-deploy

REM Update configuration files with actual values
powershell -Command "(Get-Content deploy\temp-deploy\.env.production) -replace 'your_secure_password_here', '%DB_PASSWORD%' | Set-Content deploy\temp-deploy\.env.production"
powershell -Command "(Get-Content deploy\temp-deploy\.env.production) -replace 'your_very_secure_random_key_here', '%SECRET_KEY%' | Set-Content deploy\temp-deploy\.env.production"
powershell -Command "(Get-Content deploy\temp-deploy\deploy\nginx.conf) -replace 'your-domain.com', '%DOMAIN%' | Set-Content deploy\temp-deploy\deploy\nginx.conf"

echo 📤 Uploading files to VPS...
scp -r deploy\temp-deploy %VPS_USER%@%VPS_HOST%:/opt/petrol-station

echo 🔧 Running deployment on VPS...
ssh %VPS_USER%@%VPS_HOST% "cd /opt/petrol-station && chmod +x deploy/final-deploy.sh && ./deploy/final-deploy.sh"

echo 🎉 Deployment completed!
echo 🌐 Your application will be available at: https://%DOMAIN%
echo.
echo 📋 Next steps:
echo 1. Test the application at https://%DOMAIN%
echo 2. Update DNS records if needed
echo 3. Monitor logs: ssh %VPS_USER%@%VPS_HOST% "cd /opt/petrol-station/deploy && docker-compose logs -f"
echo 4. Setup monitoring and alerts

pause
