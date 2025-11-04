# إعداد قاعدة البيانات على PlanetScale - PlanetScale Database Setup

## نظرة عامة
PlanetScale هو خدمة استضافة قاعدة بيانات MySQL مجانية تماماً مع ميزات متقدمة مثل النسخ الاحتياطي التلقائي، التوسع التلقائي، وواجهة إدارة سهلة.

## المميزات
- **مجاني تماماً**: 1 قاعدة بيانات، 1 جيجابايت تخزين، 1000 استعلام شهرياً
- **سريع وآمن**: SSL إلزامي، نسخ احتياطي تلقائي
- **سهل الاستخدام**: واجهة ويب بسيطة، دعم MySQL كامل
- **توسع تلقائي**: يتكيف مع احتياجاتك

## خطوات الإعداد

### الخطوة 1: إنشاء حساب PlanetScale
1. اذهب إلى: [https://planetscale.com](https://planetscale.com)
2. اضغط على **"Sign Up"** وأنشئ حساباً جديداً
3. أكد بريدك الإلكتروني

### الخطوة 2: إنشاء قاعدة البيانات
1. في لوحة التحكم الرئيسية، اضغط على **"Create database"**
2. أدخل اسم قاعدة البيانات: `petrolpump_management`
3. اختر المنطقة الأقرب لك (مثل: AWS us-east-1)
4. اضغط على **"Create database"**

### الخطوة 3: الحصول على بيانات الاتصال
1. في صفحة قاعدة البيانات، اضغط على **"Connect"**
2. ستجد قسم **"Connect with your application"**
3. البيانات المطلوبة:
   - **Database host**: مثل `aws.connect.psdb.cloud`
   - **Database username**: اسم المستخدم (مثل: `abcdefghijklmnop`)
   - **Database password**: كلمة المرور (قد تحتاج لإنشاء كلمة مرور جديدة)
   - **Database name**: `petrolpump_management`

### الخطوة 4: إنشاء كلمة مرور (إذا لزم الأمر)
1. في صفحة قاعدة البيانات، اذهب إلى **"Settings"** → **"Passwords"**
2. اضغط على **"New password"**
3. أدخل اسم لكلمة المرور (مثل: `app_password`)
4. اضغط على **"Create password"**
5. احفظ كلمة المرور في مكان آمن

### الخطوة 5: تحميل شهادة SSL
```bash
# في مجلد Project/deploy/
wget https://planetscale.com/assets/planetscale-ca-cert.pem
```

### الخطوة 6: إعداد ملف البيئة
أنشئ ملف `.env` في مجلد `Project/deploy/`:

```env
# Database Configuration for PlanetScale
DB_HOST=your-planetscale-host.aws.connect.psdb.cloud
DB_USER=your_planetscale_username
DB_PASSWORD=your_planetscale_password
DB_NAME=petrolpump_management
DB_PORT=3306
DB_SSL_CA=./planetscale-ca-cert.pem

# Application Configuration
SECRET_KEY=your-production-secret-key-here
APP_ENV=production
```

### الخطوة 7: تشغيل سكريبت الإعداد
```bash
cd Project/deploy/
python setup_database_hosting.py
```

### الخطوة 8: اختبار الاتصال
```bash
python setup_database_hosting.py test
```

## ملاحظات مهمة

### حدود الخطة المجانية:
- **1 قاعدة بيانات** فقط
- **1 جيجابايت تخزين**
- **1000 استعلام شهرياً**
- **لا يمكن الترقية**: إذا تجاوزت الحدود، ستحتاج للترقية للخطة المدفوعة

### أمان PlanetScale:
- **SSL إلزامي**: جميع الاتصالات مشفرة
- **نسخ احتياطي تلقائي**: يومياً
- **لا يمكن الوصول المباشر**: فقط عبر API

### استكشاف الأخطاء:

#### خطأ في الاتصال:
```
❌ Database error: Access denied
```
**الحل**: تحقق من اسم المستخدم وكلمة المرور

#### خطأ SSL:
```
❌ SSL connection error
```
**الحل**: تأكد من وجود ملف `planetscale-ca-cert.pem` ومساره الصحيح

#### خطأ في المنفذ:
```
❌ Connection timeout
```
**الحل**: PlanetScale يستخدم المنفذ 3306، تأكد من عدم وجود firewall

#### تجاوز الحدود:
```
❌ Too many connections
```
**الحل**: قلل من عدد الاستعلامات أو ارتقِ للخطة المدفوعة

## إدارة قاعدة البيانات

### الوصول لواجهة PlanetScale:
1. اذهب إلى لوحة التحكم
2. اضغط على قاعدة البيانات
3. يمكنك:
   - **استعراض الجداول**: في قسم "Tables"
   - **تشغيل استعلامات**: في قسم "Console"
   - **عرض السجلات**: في قسم "Insights"

### النسخ الاحتياطي:
- **تلقائي**: يومياً
- **يدوي**: اضغط على "Backups" → "Create backup"

## الترقية للإنتاج

عندما ينمو مشروعك:
1. **Railway**: بديل مجاني آخر مع المزيد من الموارد
2. **AWS RDS**: للإنتاج الثقيل
3. **Google Cloud SQL**: بديل قوي آخر

## الدعم والمساعدة

### موارد مفيدة:
- **التوثيق**: https://docs.planetscale.com
- **المجتمع**: https://planetscale.com/discord
- **الدعم**: support@planetscale.com

### إذا واجهت مشاكل:
1. تحقق من لوحة التحكم في PlanetScale
2. راجع logs التطبيق
3. تأكد من صحة بيانات الاتصال

---

**تم إنشاء هذا الدليل بواسطة نظام إدارة محطات الوقود**
