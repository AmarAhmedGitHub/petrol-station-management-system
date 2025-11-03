# إعداد وتشغيل نظام إدارة محطات الوقود مع الاستشعار الآلي

## 📋 نظرة عامة

تم تطوير نظام إدارة محطات الوقود مع دعم الاستشعار الآلي لقراءات مستويات الوقود في الوقت الفعلي. النظام يدعم التكامل مع أجهزة الاستشعار PTS2 و ATG مع إمكانية الرجوع للقراءات المحاكاة عند فشل الاتصال.

## 🔧 المتطلبات

### البرمجيات المطلوبة:
- Python 3.8 أو أحدث
- MySQL Server 8.0 أو أحدث
- Git (اختياري)

### المكتبات المطلوبة:
```
streamlit>=1.28.0
mysql-connector-python>=8.0.33
pandas>=2.0.0
matplotlib>=3.7.0
APScheduler==3.10.4
requests>=2.31.0
python-dotenv>=1.0.0
```

## ⚙️ إعداد البيئة

### 1. تحميل المشروع
```bash
git clone <repository-url>
cd petrol-pump-management-system/Project
```

### 2. إنشاء البيئة الافتراضية (موصى به)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. إعداد قاعدة البيانات
- قم بتثبيت MySQL Server
- أنشئ قاعدة بيانات جديدة باسم `Petrolpump_Management_Enhanced`
- تأكد من أن المستخدم `root` لديه صلاحيات الوصول

### 5. إعداد ملف البيئة (.env)

قم بإنشاء ملف `.env` في مجلد `Project` بالمحتوى التالي:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=Petrolpump_Management_Enhanced

# Sensor API Configuration
PTS2_API_URL=https://api.pts2-sensor.com/v1/readings
PTS2_API_KEY=your_pts2_api_key_here
PTS2_TIMEOUT=10

ATG_API_URL=https://api.atg-sensor.com/v1/levels
ATG_API_KEY=your_atg_api_key_here
ATG_TIMEOUT=10

# Sensor Mappings (Tank_ID -> Sensor Configuration)
SENSOR_MAPPINGS={
    "TANK001": {"type": "PTS2", "sensor_id": "PTS2_001", "pump_id": "PUMP001"},
    "TANK002": {"type": "ATG", "sensor_id": "ATG_001", "pump_id": "PUMP002"},
    "TANK003": {"type": "PTS2", "sensor_id": "PTS2_002", "pump_id": "PUMP003"}
}

# Automation Settings
RECONCILIATION_INTERVAL_HOURS=7.5
AUTOMATION_ENABLED=true
FALLBACK_TO_MOCK=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=automation.log

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8502
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# System Settings
DEFAULT_FUEL_PRICE=8.50
LOW_FUEL_ALERT_PERCENT=20
MAINTENANCE_INTERVAL_DAYS=90

# System Version and Updates Tracking
SYSTEM_VERSION=2.0.1
LAST_UPDATE=2024-12-15
LAST_UPDATE_BY=developer_name
UPDATE_NOTES=Enhanced sensor integration and error handling

# Feature Flags for Updates
SENSOR_ENHANCED_NOTIFICATIONS=true
REAL_TIME_DASHBOARD=true
AUTOMATED_BACKUP=true
ADVANCED_REPORTING=false
MAINTENANCE_SCHEDULER=false
MOBILE_APP_INTEGRATION=false
```

## 🚀 تشغيل النظام

### الطريقة الأولى: استخدام السكريبت التلقائي (موصى به)

#### Windows:
```bash
start_with_env.bat
```

#### Linux/Mac:
```bash
chmod +x start_with_env.sh
./start_with_env.sh
```

### الطريقة الثانية: التشغيل اليدوي

```bash
# تشغيل النظام
streamlit run main_app_automation.py --server.port 8502

# أو تشغيل النظام الأساسي
streamlit run app.py
```

## 🔍 فحص النظام

### اختبار الاستيراد الأساسي:
```bash
python test_basic.py
```

### اختبار النظام الآلي:
```bash
python test_automation.py
```

## 📊 الميزات الرئيسية

### 🤖 النظام الآلي:
- **قراءات الاستشعار في الوقت الفعلي**: تكامل مع PTS2 و ATG sensors
- **التسوية التلقائية**: حساب ديون الموظفين كل 7.5 ساعات
- **الرجوع للقراءات المحاكاة**: عند فشل الاتصال بالأجهزة
- **إدارة الديون**: إضافة، عرض، تسوية ديون الموظفين

### 🗄️ قاعدة البيانات المحسنة:
- جداول منفصلة للمحطات والمضخات والخزانات
- تتبع شامل للمبيعات والصيانة والتوريد
- سجل عمليات مفصل للتدقيق

### 👥 نظام المستخدمين:
- ثلاثة أنواع من المستخدمين: Admin، Owner، Employee
- صلاحيات مختلفة لكل نوع
- نظام تسجيل دخول آمن

## 🔧 إعدادات الاستشعار

### إعدادات PTS2:
- **API URL**: رابط خدمة PTS2
- **API Key**: مفتاح المصادقة
- **Timeout**: مهلة الاتصال (ثانية)

### إعدادات ATG:
- **API URL**: رابط خدمة ATG
- **API Key**: مفتاح المصادقة
- **Timeout**: مهلة الاتصال (ثانية)

### ربط الاستشعار:
```json
{
    "TANK001": {
        "type": "PTS2",
        "sensor_id": "PTS2_001",
        "pump_id": "PUMP001"
    }
}
```

## 📈 التقارير والإحصائيات

- لوحة تحكم تفاعلية مع مؤشرات الأداء
- تقارير المبيعات والأرباح
- تتبع ديون الموظفين
- إحصائيات الصيانة والوقود

## 🛠️ استكشاف الأخطاء

### مشاكل شائعة:

1. **خطأ في الاستيراد**:
   ```bash
   pip install -r requirements.txt
   ```

2. **مشكلة في قاعدة البيانات**:
   - تأكد من تشغيل MySQL Server
   - تحقق من بيانات الاتصال في `.env`
   - أعد إنشاء الجداول باستخدام `create_enhanced_db_complete.py`

3. **مشكلة في الاستشعار**:
   - تحقق من مفاتيح API
   - تأكد من اتصال الإنترنت
   - النظام سيعمل بالقراءات المحاكاة تلقائياً

4. **مشكلة في التشغيل**:
   ```bash
   # تنظيف ذاكرة التخزين المؤقت
   rm -rf __pycache__/
   rm -rf pages/__pycache__/
   rm -rf core/__pycache__/
   ```

## 📞 الدعم

للحصول على المساعدة أو الإبلاغ عن مشاكل:
- تحقق من ملفات السجل في `automation.log`
- راجع ملفات `TODO_*.md` للمهام المعلقة
- استخدم اختبارات `test_*.py` لتشخيص المشاكل

## 📝 الترخيص

هذا المشروع مطور لأغراض تعليمية وتجارية. يرجى الرجوع إلى ملف `LICENSE` للتفاصيل.

---

**تم التطوير باستخدام**: Python, Streamlit, MySQL, APScheduler
**الإصدار**: 2.0 - مع الاستشعار الآلي
