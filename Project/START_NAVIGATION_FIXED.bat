@echo off
echo ========================================
echo    نظام إدارة محطات الوقود ⛽
echo ========================================
echo.
echo ✅ تم إصلاح مشكلة التنقل!
echo.
echo المشكلة التي تم حلها:
echo - عند الضغط على زر "العودة" كان ينتقل لتسجيل الدخول
echo - الآن يعود للصفحة السابقة بشكل صحيح
echo.
echo الملفات المُحدثة:
echo 1. main_app_navigation_fixed.py (التطبيق الرئيسي)
echo 2. main_reports_navigation_fixed.py (التقارير)
echo 3. main_management_navigation_fixed.py (الإدارة)
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
echo ✅ تم إصلاح مشكلة التنقل:
echo    - أزرار العودة تعمل بشكل صحيح
echo    - حفظ الصفحة السابقة في الذاكرة
echo    - عدم إعادة تشغيل التطبيق
echo.
echo للإغلاق: اضغط Ctrl+C في النافذة السوداء
echo ========================================
echo.

streamlit run main_app_navigation_fixed.py

pause
