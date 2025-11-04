# إعداد قاعدة البيانات على Hostinger - Hostinger Database Setup

## كيفية الحصول على بيانات قاعدة البيانات من Hostinger

### الخطوة 1: الدخول إلى لوحة تحكم Hostinger

1. اذهب إلى: [https://www.hostinger.com](https://www.hostinger.com)
2. اضغط على "Login" في أعلى الصفحة
3. أدخل بيانات حسابك (البريد الإلكتروني وكلمة المرور)

### الخطوة 2: الوصول إلى قسم قواعد البيانات

#### لـ VPS Hosting:
1. من لوحة التحكم الرئيسية، اضغط على **"VPS"**
2. اختر VPS الخاص بك من القائمة
3. اضغط على **"Manage VPS"**
4. في لوحة VPS، ابحث عن **"Databases"** أو **"MySQL"**

#### لـ Shared Hosting:
1. من لوحة التحكم الرئيسية، اضغط على **"Hosting"**
2. اختر موقعك من القائمة
3. اضغط على **"Manage"** بجانب اسم النطاق
4. في الشريط الجانبي، اضغط على **"Databases"**
5. ثم اضغط على **"MySQL Databases"**

### الخطوة 3: إنشاء قاعدة بيانات جديدة

1. في صفحة MySQL Databases، اضغط على **"Create Database"**
2. أدخل اسم قاعدة البيانات: `Petrolpump_Management_Enhanced`
3. اختر **"utf8mb4_general_ci"** كـ Collation
4. اضغط على **"Create"**

### الخطوة 4: إنشاء مستخدم قاعدة البيانات

1. في نفس الصفحة، اذهب إلى قسم **"MySQL Users"**
2. اضغط على **"Create User"**
3. أدخل اسم المستخدم (مثل: `petrol_user`)
4. أدخل كلمة مرور قوية
5. اضغط على **"Create User"**

### الخطوة 5: ربط المستخدم بالقاعدة

1. في قسم **"User Privileges"** أو **"Manage User Privileges"**
2. اختر المستخدم الذي أنشأته
3. اختر قاعدة البيانات `Petrolpump_Management_Enhanced`
4. حدد جميع الصلاحيات (Check All)
5. اضغط على **"Save"** أو **"Update"**

### الخطوة 6: الحصول على بيانات الاتصال

بعد إنشاء قاعدة البيانات والمستخدم، ستجد البيانات التالية:

#### 📍 **Database Host** (الخادم):
- عادةً يكون: `mysql.hostinger.com` أو `your-domain.com`
- أو عنوان IP محدد لخادم MySQL
- **مثال:** `mysql-123456.hostinger.com`

#### 👤 **Database Username** (اسم المستخدم):
- الاسم الذي أدخلته عند إنشاء المستخدم
- **مثال:** `u123456789_petrol_user`

#### 🔑 **Database Password** (كلمة المرور):
- كلمة المرور التي حددتها للمستخدم

#### 🗄️ **Database Name** (اسم قاعدة البيانات):
- `Petrolpump_Management_Enhanced`

#### 🔌 **Port** (المنفذ):
- عادةً: `3306` (الافتراضي لـ MySQL)

### الخطوة 7: نسخ البيانات إلى ملف .env

أنشئ ملف `.env` بالمحتوى التالي:

```env
# Database Configuration
DB_HOST=mysql-123456.hostinger.com
DB_USER=u123456789_petrol_user
DB_PASSWORD=your_secure_password_here
DB_NAME=Petrolpump_Management_Enhanced
DB_PORT=3306

# Application Configuration
SECRET_KEY=your-production-secret-key-here
APP_ENV=production
DEBUG=false

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

## 🔍 كيفية العثور على البيانات في لوحة Hostinger

### إذا كنت تستخدم Shared Hosting:
1. اذهب إلى **Files → File Manager**
2. افتح مجلد **public_html** أو الموقع الخاص بك
3. ابحث عن ملفات مثل `wp-config.php` (إذا كان WordPress) أو ملفات التطبيق الأخرى
4. غالباً ما تحتوي على بيانات قاعدة البيانات

### إذا كنت تستخدم VPS:
1. في لوحة VPS، اضغط على **"Access Details"**
2. ستجد بيانات الاتصال بقاعدة البيانات

## ⚠️ ملاحظات مهمة

### أمان قاعدة البيانات:
- **لا تستخدم** كلمة مرور ضعيفة
- **لا تستخدم** المستخدم `root` للتطبيقات
- **فعل** النسخ الاحتياطي التلقائي في Hostinger

### حدود Hostinger:
- **Shared Hosting**: قد يكون هناك حدود على عدد قواعد البيانات
- **VPS**: حدود أعلى، لكن تأكد من موارد الخادم

### استكشاف الأخطاء:
- **خطأ في الاتصال**: تحقق من اسم الخادم والمنفذ
- **خطأ في الصلاحيات**: تأكد من ربط المستخدم بالقاعدة
- **خطأ في الترميز**: تأكد من استخدام `utf8mb4`

## 📞 الدعم الفني

إذا واجهت صعوبة في العثور على البيانات:
1. اتصل بدعم Hostinger
2. أرسل لقطة شاشة من لوحة التحكم
3. حدد نوع الاستضافة (Shared/VPS)

## 🔄 الخطوة التالية

بعد الحصول على بيانات قاعدة البيانات:
1. أدخل البيانات في ملف `.env`
2. شغل سكريبت إعداد قاعدة البيانات:
   ```bash
   python3 setup_database_hosting.py
   ```
3. ارفع التطبيق وشغله

---

**تم إنشاء هذا الدليل بواسطة نظام إدارة محطات الوقود**
