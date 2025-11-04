# نشر نظام إدارة محطات الوقود على Streamlit Cloud

## نظرة عامة
هذا الدليل يوضح كيفية نشر نظام إدارة محطات الوقود على Streamlit Cloud مجاناً.

## المتطلبات
- حساب GitHub
- حساب Streamlit Cloud
- مشروع محمل على GitHub

## خطوات النشر

### 1. تحضير الملفات
تأكد من وجود الملفات التالية في المشروع:

#### `packages.txt`
```
mysqlclient
default-libmysqlclient-dev
build-essential
```

#### `.streamlit/config.toml`
```toml
[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false

[theme]
base = "light"
primaryColor = "#0d6efd"
```

#### `requirements.txt` (محدث)
```
streamlit>=1.28.0
mysql-connector-python>=8.0.33
pymysql>=1.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
matplotlib>=3.7.0
numpy>=1.24.0
plotly>=5.15.0
pillow>=10.0.0
APScheduler==3.10.4
reportlab>=4.0.0
flask>=2.3.0
flask-cors>=4.0.0
bcrypt>=4.0.1
tenacity>=8.2.0
mysqlclient>=2.1.0
protobuf>=3.20.0
```

### 2. رفع المشروع إلى GitHub
```bash
git add .
git commit -m "Add Streamlit Cloud deployment files"
git push origin main
```

### 3. النشر على Streamlit Cloud

#### الخطوة 1: إنشاء التطبيق
1. اذهب إلى: https://share.streamlit.io
2. اضغط على "New app"
3. اختر المستودع والفرع

#### الخطوة 2: إعداد التطبيق
- **Repository**: `your-username/your-repo-name`
- **Branch**: `main`
- **Main file path**: `Project/main_app.py`
- **App URL**: اتركه فارغاً (سيتم إنشاؤه تلقائياً)

#### الخطوة 3: إضافة متغيرات البيئة
في إعدادات التطبيق، أضف المتغيرات التالية:

```
DB_HOST=sql.freedb.tech
DB_USER=freedb_free_amar
DB_PASSWORD=m*$xxJtz7dYrn7d
DB_NAME=freedb_petrolpump_management
DB_PORT=3306
```

### 4. بدء النشر
اضغط على "Deploy!" لبدء عملية النشر.

## استكشاف الأخطاء

### خطأ في الاتصال بقاعدة البيانات
```
ModuleNotFoundError: No module named 'mysqlclient'
```
**الحل**: تأكد من وجود `mysqlclient` في `packages.txt`

### خطأ في المنفذ
```
Port 8501 is already in use
```
**الحل**: غير المنفذ في `.streamlit/config.toml`

### خطأ في الذاكرة
```
MemoryError
```
**الحل**: قلل من استخدام الذاكرة أو ارتقِ للخطة المدفوعة

## بيانات الدخول
بعد النشر بنجاح:
- **الرابط**: https://your-app-name.streamlit.app
- **اسم المستخدم**: `admin`
- **كلمة المرور**: `admin123`

## المميزات المتاحة
- ✅ لوحة تحكم شاملة
- ✅ إدارة المحطات والمضخات
- ✅ نظام المحاسبة الكامل
- ✅ إدارة الموظفين والعملاء
- ✅ التقارير والإحصائيات
- ✅ مراقبة المستشعرات
- ✅ نظام الأمان والمصادقة

## الدعم والمساعدة
إذا واجهت أي مشاكل:
1. تحقق من logs النشر
2. تأكد من صحة متغيرات البيئة
3. تحقق من إعدادات قاعدة البيانات

---
**تم إنشاء هذا الدليل بواسطة نظام إدارة محطات الوقود**