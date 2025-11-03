#!/bin/bash

# نظام إدارة محطات الوقود - النسخة المحسنة
# ملف تشغيل للأنظمة المبنية على Unix/Linux/Mac

echo "========================================"
echo "   نظام إدارة محطات الوقود"
echo "   النسخة المحسنة مع التعيينات"
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
echo "🗄️ إنشاء قاعدة البيانات المحسنة..."
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
echo "========================================"
echo

# تشغيل Streamlit
streamlit run main_app_permissions_fixed.py --server.port 8501 --server.address 0.0.0.0

echo
echo "تم إيقاف النظام"
