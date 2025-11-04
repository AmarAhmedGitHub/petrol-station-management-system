# قاعدة البيانات للاستضافة - Database Hosting Guide

## نظرة عامة
هذا الدليل يوضح كيفية استضافة قاعدة البيانات لنظام إدارة محطات الوقود على خوادم MySQL خارجية مثل Hostinger، AWS RDS، أو DigitalOcean.

## المتطلبات
- خادم MySQL خارجي (Hostinger VPS، AWS RDS، إلخ)
- بيانات الاتصال بالقاعدة (Host، User، Password، Database Name)
- Python 3.7+ مع مكتبات mysql-connector و python-dotenv

## خطوات الإعداد

### 1. إعداد ملف البيئة
```bash
# في مجلد Project/deploy/
cp .env.example .env
```

قم بتحديث ملف `.env` بالبيانات الصحيحة:
```env
# Database Configuration for Hosting
DB_HOST=your-hostinger-mysql-host.com
DB_USER=your_database_user
DB_PASSWORD=your_secure_password
DB_NAME=Petrolpump_Management_Enhanced
DB_PORT=3306

# Application Configuration
SECRET_KEY=your-secret-key-here
APP_ENV=production
```

### 2. تشغيل سكريبت إعداد القاعدة
```bash
cd Project/deploy/
python setup_database_hosting.py
```

### 3. اختبار الاتصال
```bash
python setup_database_hosting.py test
```

## هيكل القاعدة

### الجداول الأساسية
- `FuelTypes` - أنواع الوقود
- `PetrolStations` - محطات الوقود
- `Employees` - الموظفين
- `FuelTanks` - خزانات الوقود
- `FuelPumps` - مضخات الوقود
- `Customers` - العملاء
- `Invoices` - الفواتير
- `FuelSupply` - توريد الوقود

### جداول المحاسبة
- `ChartOfAccounts` - دليل الحسابات
- `JournalEntries` - القيود اليومية
- `ReceiptVouchers` - سندات القبض
- `PaymentVouchers` - سندات الصرف

### جداول الصيانة والمراقبة
- `PumpMaintenance` - صيانة المضخات
- `TankMaintenance` - صيانة الخزانات
- `SensorReadings` - قراءات المستشعرات
- `AuditLog` - سجل العمليات

## البيانات الافتراضية

يتم إدراج البيانات التالية تلقائياً:
- أنواع الوقود الأساسية (بنزين 95، 98، ديزل، كيروسين)
- إعدادات النظام الافتراضية
- دليل الحسابات الأساسي
- إعدادات الضرائب

## إعدادات الأمان

### إنشاء مستخدم قاعدة منفصل (مستحسن)
```sql
CREATE USER 'petrol_user'@'%' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON Petrolpump_Management_Enhanced.* TO 'petrol_user'@'%';
FLUSH PRIVILEGES;
```

### نسخ احتياطي تلقائي
```sql
-- إنشاء مهمة نسخ احتياطي يومي
mysqldump -u petrol_user -p Petrolpump_Management_Enhanced > backup_$(date +%Y%m%d).sql
```

## استكشاف الأخطاء

### خطأ في الاتصال
```
❌ Database error: Access denied for user
```
**الحل:** تحقق من بيانات الاتصال في ملف `.env`

### خطأ في إنشاء الجداول
```
❌ Table already exists
```
**الحل:** السكريبت يستخدم `IF NOT EXISTS` لذا هذا طبيعي

### خطأ في الترميز
```
❌ Incorrect string value
```
**الحل:** تأكد من أن القاعدة تستخدم `utf8mb4`

## الأداء والتحسين

### فهرسة الجداول
```sql
-- فهرسة الجداول الأكثر استخداماً
CREATE INDEX idx_invoices_date ON Invoices(Invoice_Date);
CREATE INDEX idx_sensor_readings_timestamp ON SensorReadings(Timestamp);
```

### تحسين الاستعلامات
- استخدم `EXPLAIN` لتحليل الاستعلامات البطيئة
- تجنب الاستعلامات الكبيرة بدون فهرسة
- استخدم `LIMIT` في الاستعلامات الكبيرة

## النسخ الاحتياطي

### نسخ احتياطي كامل
```bash
mysqldump -u petrol_user -p Petrolpump_Management_Enhanced > full_backup.sql
```

### نسخ احتياطي تفاضلي
```bash
mysqldump -u petrol_user -p --single-transaction Petrolpump_Management_Enhanced > incremental_backup.sql
```

### استعادة من النسخة الاحتياطية
```bash
mysql -u petrol_user -p Petrolpump_Management_Enhanced < backup.sql
```

## مراقبة الأداء

### مراقبة استخدام القرص
```sql
SELECT
    table_name,
    ROUND(data_length/1024/1024, 2) as data_mb,
    ROUND(index_length/1024/1024, 2) as index_mb
FROM information_schema.tables
WHERE table_schema = 'Petrolpump_Management_Enhanced'
ORDER BY data_length DESC;
```

### مراقبة الاستعلامات البطيئة
```sql
-- تفعيل سجل الاستعلامات البطيئة
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2; -- ثانيتان
```

## الدعم والمساعدة

إذا واجهت أي مشاكل:
1. تحقق من logs التطبيق
2. اختبر الاتصال بالقاعدة
3. راجع إعدادات الـ firewall
4. تأكد من صلاحيات المستخدم

---

**تم إنشاء هذا الدليل بواسطة نظام إدارة محطات الوقود المتقدم**
