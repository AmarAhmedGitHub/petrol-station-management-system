#!/bin/bash

# نظام إدارة محطات الوقود - النسخة المستعادة
# ملف تشغيل للأنظمة المبنية على Unix/Linux/Mac

echo "========================================"
echo "   نظام إدارة محطات الوقود ⛽"
echo "   النسخة المستعادة مع نظام التنقل"
echo "========================================"
echo

# التحقق من وجود Python
if ! command -v python &> /dev/null; then
    echo "❌ خطأ: Python غير مثبت"
    echo "يرجى تثبيت Python 3.8 أو أحدث"
    exit 1
fi

echo "✅ Python متاح"

# التحقق من المتطلبات
echo "🔍 التحقق من المتطلبات..."
python -c "import streamlit, mysql.connector, pandas, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ خطأ: المتطلبات غير مثبتة"
    echo "🔧 تثبيت المتطلبات..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ فشل في تثبيت المتطلبات"
        exit 1
    fi
fi

echo "✅ المتطلبات متاحة"

# إنشاء قاعدة البيانات
echo "🗄️ إنشاء قاعدة البيانات..."
python Create_database.py
if [ $? -ne 0 ]; then
    echo "❌ خطأ في إنشاء قاعدة البيانات"
    exit 1
fi

echo "✅ قاعدة البيانات جاهزة"

# بدء تشغيل النظام
echo "🚀 بدء تشغيل النظام..."
echo "========================================"
echo "🌐 سيتم فتح النظام في المتصفح..."
echo "📝 للإيقاف اضغط Ctrl+C"
echo "✅ تم استعادة نظام التنقل:"
echo "   - القائمة الجانبية متاحة"
echo "   - أزرار التنقل تعمل بشكل صحيح"
echo "   - نظام الصلاحيات مفعل"
echo "========================================"
echo

# تشغيل Streamlit
streamlit run main_app_navigation_restored.py --server.port 8501 --server.address 0.0.0.0

echo
echo "تم إيقاف النظام"
