#!/usr/bin/env python3
"""
Streamlit Hosting Setup for Petrol Station Management System
Configures the application for direct hosting on Hostinger without Docker
"""

import os
import sys
import shutil
from pathlib import Path

def setup_streamlit_hosting():
    """Setup Streamlit application for hosting"""

    print("🚀 Setting up Streamlit Hosting for Petrol Station Management System")
    print("=" * 70)

    # Get the project root directory
    project_root = Path(__file__).parent.parent
    deploy_dir = Path(__file__).parent

    print(f"📁 Project root: {project_root}")
    print(f"📁 Deploy directory: {deploy_dir}")

    # Step 1: Create hosting directory structure
    hosting_dir = deploy_dir / "streamlit_hosting"
    hosting_dir.mkdir(exist_ok=True)

    print("📂 Creating hosting directory structure...")

    # Step 2: Copy essential files
    files_to_copy = [
        'main_app.py',
        'app_enhanced.py',
        'requirements.txt',
        'core/',
        'pages/',
        'tests/',
        'scripts/',
        '.env.example'
    ]

    for file_path in files_to_copy:
        src = project_root / file_path
        dst = hosting_dir / file_path

        if src.is_file():
            shutil.copy2(src, dst)
            print(f"✅ Copied {file_path}")
        elif src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"✅ Copied directory {file_path}")

    # Step 3: Create Streamlit configuration
    create_streamlit_config(hosting_dir)

    # Step 4: Create production requirements
    create_production_requirements(hosting_dir)

    # Step 5: Create startup script
    create_startup_script(hosting_dir)

    # Step 6: Create .env template for production
    create_env_template(hosting_dir)

    print("\n✅ Streamlit hosting setup completed!")
    print(f"📁 Hosting files created in: {hosting_dir}")
    print("\n📋 Next steps:")
    print("1. Upload the 'streamlit_hosting' folder to Hostinger")
    print("2. Set up the database using database_hosting.sql")
    print("3. Update .env file with your database credentials")
    print("4. Run: python startup.py")

    return hosting_dir

def create_streamlit_config(hosting_dir):
    """Create Streamlit configuration file"""

    config_content = """[global]
developmentMode = false
dataFrameSerialization = "legacy"

[logger]
level = "INFO"

[client]
showSidebarNavigation = true
showErrorDetails = false

[server]
headless = true
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200
maxMessageSize = 200
enableWebsocketCompression = true

[browser]
gatherUsageStats = false
"""

    config_file = hosting_dir / ".streamlit" / "config.toml"
    config_file.parent.mkdir(exist_ok=True)

    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)

    print("✅ Created Streamlit config")

def create_production_requirements(hosting_dir):
    """Create production requirements file"""

    prod_requirements = """# Production Requirements for Streamlit Hosting
streamlit>=1.28.0
mysql-connector-python>=8.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
plotly>=5.15.0
bcrypt>=4.0.0
cryptography>=41.0.0
pillow>=10.0.0
requests>=2.31.0
schedule>=1.2.0
apscheduler>=3.10.0
openpyxl>=3.1.0
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.11.0
scikit-learn>=1.3.0
xgboost>=1.7.0
joblib>=1.3.0
"""

    req_file = hosting_dir / "requirements_production.txt"
    with open(req_file, 'w', encoding='utf-8') as f:
        f.write(prod_requirements)

    print("✅ Created production requirements")

def create_startup_script(hosting_dir):
    """Create startup script for production"""

    startup_content = """#!/usr/bin/env python3
\"\"\"
Startup script for Petrol Station Management System on Hostinger
\"\"\"

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Starting Petrol Station Management System")
    print("=" * 50)

    # Set production environment
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'

    # Check if .env exists
    if not Path('.env').exists():
        print("⚠️  No .env file found. Please create one with your database credentials.")
        print("   Copy .env.example to .env and update the values.")
        return

    # Check database connection
    try:
        from core.database import test_connection
        if test_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed. Please check your .env file.")
            return
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return

    # Start Streamlit
    print("🌐 Starting Streamlit server...")
    print("📱 Access your application at: http://your-domain.com:8501")

    try:
        # Run streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "main_app.py",
               "--server.port", "8501",
               "--server.address", "0.0.0.0",
               "--server.headless", "true",
               "--browser.gatherUsageStats", "false"]

        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        print("\\n👋 Shutting down...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""

    startup_file = hosting_dir / "startup.py"
    with open(startup_file, 'w', encoding='utf-8') as f:
        f.write(startup_content)

    # Make startup script executable
    os.chmod(startup_file, 0o755)

    print("✅ Created startup script")

def create_env_template(hosting_dir):
    """Create .env template for production"""

    env_content = """# Production Environment Configuration
# Update these values with your Hostinger database credentials

# Database Configuration
DB_HOST=your-hostinger-mysql-host.com
DB_USER=your_database_username
DB_PASSWORD=your_secure_password
DB_NAME=Petrolpump_Management_Enhanced
DB_PORT=3306

# Application Configuration
SECRET_KEY=your-production-secret-key-here
APP_ENV=production
DEBUG=false

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Optional: Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional: Sensor API Configuration
SENSOR_API_URL=https://api.your-sensor-provider.com
SENSOR_API_KEY=your-sensor-api-key

# Optional: Backup Configuration
BACKUP_ENABLED=true
BACKUP_FREQUENCY=daily
BACKUP_RETENTION_DAYS=30
"""

    env_file = hosting_dir / ".env.production"
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)

    print("✅ Created production .env template")

def create_hostinger_upload_script(hosting_dir):
    """Create script to help with Hostinger upload"""

    upload_content = """#!/bin/bash
# Hostinger Upload Script for Petrol Station Management System
# Run this script from your local machine to upload files to Hostinger

echo "📤 Uploading Petrol Station Management System to Hostinger"
echo "========================================================="

# Configuration - Update these paths
HOSTINGER_USER="your-hostinger-username"
HOSTINGER_HOST="your-hostinger-domain.com"
REMOTE_PATH="/public_html/petrol-station"  # or your preferred path

echo "🔗 Connecting to Hostinger..."
echo "📁 Uploading files..."

# Upload files using rsync (more efficient than scp)
rsync -avz --delete \\
    --exclude='.git' \\
    --exclude='__pycache__' \\
    --exclude='*.pyc' \\
    --exclude='.env' \\
    --exclude='*.log' \\
    ./streamlit_hosting/ \\
    $HOSTINGER_USER@$HOSTINGER_HOST:$REMOTE_PATH/

if [ $? -eq 0 ]; then
    echo "✅ Upload completed successfully!"
    echo ""
    echo "📋 Next steps on Hostinger:"
    echo "1. SSH into your Hostinger account"
    echo "2. Navigate to: cd $REMOTE_PATH"
    echo "3. Copy .env.production to .env and update credentials"
    echo "4. Run database setup: python ../deploy/setup_database_hosting.py"
    echo "5. Start the application: python startup.py"
    echo ""
    echo "🌐 Your app will be available at: https://$HOSTINGER_HOST:8501"
else
    echo "❌ Upload failed. Please check your credentials and try again."
fi
"""

    upload_file = hosting_dir.parent / "upload_to_hostinger.sh"
    with open(upload_file, 'w', encoding='utf-8') as f:
        f.write(upload_content)

    # Make executable
    os.chmod(upload_file, 0o755)

    print("✅ Created Hostinger upload script")

if __name__ == "__main__":
    hosting_dir = setup_streamlit_hosting()
    create_hostinger_upload_script(hosting_dir)

    print("\n🎉 Setup complete! Ready for Hostinger deployment.")
    print("\n📁 Files created:")
    print(f"   - {hosting_dir}/ (complete application)")
    print(f"   - {hosting_dir.parent}/upload_to_hostinger.sh (upload script)")
    print("   - database_hosting.sql (database schema)")
    print("   - setup_database_hosting.py (database setup)")
