#!/usr/bin/env python3
"""
Startup script for Petrol Station Management System on Hostinger
"""

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
        print("\n👋 Shutting down...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
