#!/bin/bash
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
rsync -avz --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='*.log' \
    ./streamlit_hosting/ \
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
