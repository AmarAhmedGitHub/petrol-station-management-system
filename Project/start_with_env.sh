#!/bin/bash

echo "========================================"
echo "    نظام إدارة محطات الوقود"
echo "    مع الاستشعار الآلي"
echo "========================================"
echo

# Change to the script directory
cd "$(dirname "$0")"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ ملف .env غير موجود!"
    echo "يرجى إنشاء ملف .env بالإعدادات المطلوبة"
    read -p "اضغط Enter للمتابعة..."
    exit 1
fi

echo "✅ تم العثور على ملف .env"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python غير مثبت!"
    read -p "اضغط Enter للمتابعة..."
    exit 1
fi

echo "✅ Python مثبت"

# Install/update requirements
echo "📦 تثبيت المتطلبات..."
pip install -r requirements.txt

# Check if MySQL is running (basic check)
echo "🗄️ فحص قاعدة البيانات..."
python -c "import mysql.connector; conn = mysql.connector.connect(host='localhost', user='root', password=''); print('✅ MySQL متصل'); conn.close()" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ تحذير: لا يمكن الاتصال بـ MySQL - سيتم تشغيل النظام مع البيانات المحاكاة فقط"
fi

echo
echo "🚀 تشغيل النظام..."
echo "للوصول للنظام: http://localhost:8502"
echo "لإيقاف النظام اضغط Ctrl+C"
echo

# Start the application
streamlit run main_app_automation.py --server.port 8502 --server.headless true
