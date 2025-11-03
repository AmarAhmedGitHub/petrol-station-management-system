@echo off
echo ========================================
echo    نظام إدارة محطات الوقود
echo    مع الاستشعار الآلي
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if .env file exists
if not exist ".env" (
    echo ❌ ملف .env غير موجود!
    echo يرجى إنشاء ملف .env بالإعدادات المطلوبة
    pause
    exit /b 1
)

echo ✅ تم العثور على ملف .env

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت!
    pause
    exit /b 1
)

echo ✅ Python مثبت

REM Install/update requirements
echo 📦 تثبيت المتطلبات...
pip install -r requirements.txt

REM Check if MySQL is running (basic check)
echo 🗄️ فحص قاعدة البيانات...
python -c "import mysql.connector; conn = mysql.connector.connect(host='localhost', user='root', password=''); print('✅ MySQL متصل'); conn.close()" 2>nul
if errorlevel 1 (
    echo ⚠️ تحذير: لا يمكن الاتصال بـ MySQL - سيتم تشغيل النظام مع البيانات المحاكاة فقط
)

echo.
echo 🚀 تشغيل النظام...
echo للوصول للنظام: http://localhost:8502
echo لإيقاف النظام اضغط Ctrl+C
echo.

REM Start the application
streamlit run main_app_automation.py --server.port 8502 --server.headless true

pause
