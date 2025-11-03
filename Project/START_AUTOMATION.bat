@echo off
chcp 65001 >nul
title نظام إدارة محطات الوقود - مع الاستشعار الآلي
echo ========================================
echo    نظام إدارة محطات الوقود
echo    مع الاستشعار الآلي PTS2/ATG
echo ========================================
echo.

echo [1] بدء تشغيل النظام مع الاستشعار الآلي...
echo.

cd /d "%~dp0"

echo [2] التحقق من المتطلبات...
python -c "import streamlit, mysql.connector, pandas, plotly, requests, apscheduler" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ❌ خطأ: المتطلبات غير مثبتة
    echo يرجى تشغيل: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [3] إنشاء قاعدة البيانات المحسنة...
python Create_database.py

echo [4] بدء تشغيل النظام مع الاستشعار الآلي...
echo.
echo 🌐 سيتم فتح النظام في المتصفح...
echo 🤖 النظام الآلي: التسوية كل 7.5 ساعات
echo 📝 للإغلاق اضغط Ctrl+C
echo.
echo ========================================
echo.

streamlit run main_app_automation.py --server.port 8502 --server.address 0.0.0.0

pause
