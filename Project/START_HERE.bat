@echo off
echo ========================================
echo    نظام إدارة محطات الوقود ⛽
echo ========================================
echo.
echo تم إنشاء هذا الملف لتسهيل تشغيل النظام
echo.
echo الملفات المتاحة:
echo 1. main_app_login_fixed.py (الأحدث - واجهة تسجيل دخول محسنة)
echo 2. main_app_completely_fixed.py (مصحح بالكامل)
echo 3. main_app_fixed.py (مصحح)
echo.
echo يُنصح باستخدام main_app_login_fixed.py لأفضل تجربة
echo.
echo ========================================
echo.

cd /d "%~dp0"

echo جاري التحقق من المتطلبات...
python --version >nul 2>&1
if errorlevel 1 (
    echo خطأ: Python غير مثبت!
    echo يرجى تثبيت Python 3.8 أو أحدث
    pause
    exit /b 1
)

echo جاري التحقق من Streamlit...
streamlit --version >nul 2>&1
if errorlevel 1 (
    echo Streamlit غير مثبت. جاري التثبيت...
    pip install streamlit
    if errorlevel 1 (
        echo خطأ في تثبيت Streamlit!
        pause
        exit /b 1
    )
)

echo جاري تثبيت المتطلبات الأخرى...
pip install -r requirements.txt
if errorlevel 1 (
    echo خطأ في تثبيت المتطلبات!
    pause
    exit /b 1
)

echo.
echo ========================================
echo    تشغيل النظام...
echo ========================================
echo.
echo سيتم فتح النظام في المتصفح تلقائياً
echo العنوان: http://localhost:8501
echo.
echo للإغلاق: اضغط Ctrl+C في النافذة السوداء
echo ========================================
echo.

streamlit run main_app_login_fixed.py

pause
