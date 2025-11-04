#!/usr/bin/env python3
"""
Hostinger Quick Start Script
Automated setup for Petrol Station Management System on Hostinger
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def quick_start():
    """Quick start setup for Hostinger"""

    print("🚀 Hostinger Quick Start - Petrol Station Management System")
    print("=" * 65)

    # Check if we're on Hostinger (basic check)
    try:
        with open('/proc/version', 'r') as f:
            version = f.read().lower()
            if 'hostinger' not in version:
                print("⚠️  Warning: This doesn't appear to be a Hostinger server.")
                print("   Continuing anyway...")
    except:
        pass

    # Step 1: Install system dependencies
    print("📦 Installing system dependencies...")
    install_system_deps()

    # Step 2: Setup Python environment
    print("🐍 Setting up Python environment...")
    setup_python_env()

    # Step 3: Install Python packages
    print("📚 Installing Python packages...")
    install_python_packages()

    # Step 4: Setup database
    print("🗄️  Setting up database...")
    setup_database()

    # Step 5: Configure environment
    print("⚙️  Configuring environment...")
    configure_environment()

    # Step 6: Test setup
    print("🧪 Testing setup...")
    test_setup()

    # Step 7: Start application
    print("🌐 Starting application...")
    start_application()

    print("\n🎉 Setup completed successfully!")
    print("\n📋 Important Information:")
    print("- Application URL: http://your-domain.com:8501")
    print("- Default login: admin / admin123")
    print("- Database: Hosted on external MySQL")
    print("- Logs: Check ~/.streamlit/logs/")

def install_system_deps():
    """Install system dependencies"""

    deps = [
        "python3-dev",
        "build-essential",
        "libmysqlclient-dev",
        "pkg-config",
        "curl",
        "wget"
    ]

    try:
        # Update package list
        subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)

        # Install dependencies
        subprocess.run(["sudo", "apt", "install", "-y"] + deps, check=True, capture_output=True)

        print("✅ System dependencies installed")

    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not install system dependencies: {e}")
        print("   Continuing with setup...")

def setup_python_env():
    """Setup Python virtual environment"""

    try:
        # Check Python version
        result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
        print(f"   Python version: {result.stdout.strip()}")

        # Upgrade pip
        subprocess.run(["python3", "-m", "pip", "install", "--upgrade", "pip"], check=True, capture_output=True)

        print("✅ Python environment ready")

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup Python environment: {e}")
        sys.exit(1)

def install_python_packages():
    """Install Python packages"""

    try:
        # Install requirements
        if Path("requirements_production.txt").exists():
            subprocess.run(["pip3", "install", "-r", "requirements_production.txt"], check=True)
        else:
            # Fallback to main requirements
            subprocess.run(["pip3", "install", "-r", "requirements.txt"], check=True)

        print("✅ Python packages installed")

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python packages: {e}")
        sys.exit(1)

def setup_database():
    """Setup database connection"""

    if not Path(".env").exists():
        print("⚠️  No .env file found. Creating template...")

        env_content = """# Database Configuration - UPDATE THESE VALUES
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
"""

        with open(".env", "w") as f:
            f.write(env_content)

        print("✅ Created .env template")
        print("⚠️  IMPORTANT: Update .env file with your database credentials!")
        input("Press Enter after updating .env file...")

    # Test database connection
    try:
        from core.database_enhanced import get_connection

        conn = get_connection()
        if conn:
            conn.close()
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            print("   Please check your .env file credentials")
            return False

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

    return True

def configure_environment():
    """Configure application environment"""

    # Create necessary directories
    os.makedirs(".streamlit", exist_ok=True)

    # Create Streamlit config
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

    with open(".streamlit/config.toml", "w") as f:
        f.write(config_content)

    print("✅ Environment configured")

def test_setup():
    """Test the setup"""

    try:
        # Test imports
        import streamlit as st
        import mysql.connector
        import pandas as pd

        print("✅ Core imports successful")

        # Test database connection
        from core.database_enhanced import get_connection
        conn = get_connection()
        if conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM FuelTypes")
            result = c.fetchone()
            print(f"✅ Database test successful - {result[0]} fuel types found")
            conn.close()
        else:
            print("❌ Database test failed")
            return False

        return True

    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def start_application():
    """Start the Streamlit application"""

    try:
        print("🚀 Starting Petrol Station Management System...")
        print("📱 Application will be available at: http://your-domain.com:8501")
        print("   (Replace 'your-domain.com' with your actual domain)")
        print("")
        print("Default login credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("")
        print("Press Ctrl+C to stop the application")
        print("-" * 50)

        # Start Streamlit
        cmd = [
            "streamlit", "run", "main_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]

        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start application: {e}")
        print("💡 Try running: python3 startup.py")

def create_service():
    """Create systemd service for auto-start"""

    service_content = f"""[Unit]
Description=Petrol Station Management System
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'www-data')}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} startup.py
Restart=always
RestartSec=5

Environment=PATH={os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin')}

[Install]
WantedBy=multi-user.target
"""

    service_path = "/etc/systemd/system/petrol-station.service"

    try:
        with open(service_path, "w") as f:
            f.write(service_content)

        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "petrol-station"], check=True)

        print("✅ Systemd service created")
        print("   Start with: sudo systemctl start petrol-station")
        print("   Check status: sudo systemctl status petrol-station")

    except Exception as e:
        print(f"⚠️  Could not create systemd service: {e}")

if __name__ == "__main__":
    try:
        quick_start()
        create_service()
    except KeyboardInterrupt:
        print("\n👋 Setup interrupted by user")
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
