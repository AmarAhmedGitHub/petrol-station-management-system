# نظام إدارة محطات الوقود - الوثائق التقنية

## 📋 نظرة عامة

نظام إدارة محطات الوقود هو تطبيق ويب شامل مبني باستخدام Streamlit و MySQL لإدارة عمليات محطات الوقود بطريقة متكاملة مع دعم الاستشعار الآلي والمحاسبة.

## 🏗️ البنية التقنية

### المكونات الأساسية

```
Project/
├── main_app.py              # التطبيق الرئيسي الموحد
├── core/                    # النواة الأساسية للنظام
│   ├── app_config.py        # إعدادات التطبيق
│   ├── auth_manager.py      # إدارة المصادقة والصلاحيات
│   ├── page_router.py       # توجيه الصفحات
│   ├── safe_html.py         # أدوات HTML آمنة
│   ├── database_enhanced.py # قاعدة البيانات المحسنة
│   ├── automation.py        # النظام الآلي
│   ├── sensor_api.py        # واجهة الاستشعار
│   ├── accounting_system.py # نظام المحاسبة
│   ├── design_system.py     # نظام التصميم
│   └── ui.py                # واجهة المستخدم
├── pages/                   # صفحات التطبيق
│   ├── auth/                # المصادقة
│   ├── dashboard/           # لوحة التحكم
│   ├── management/          # الإدارة
│   ├── accounting/          # المحاسبة
│   └── reports/             # التقارير
├── tests/                   # الاختبارات
├── scripts/                 # السكريبتات المساعدة
├── docs/                    # الوثائق
└── backup/                  # النسخ الاحتياطية
```

## 🚀 التثبيت والتشغيل

### المتطلبات الأساسية

- Python 3.8+
- MySQL 8.0+
- pip (مدير الحزم)

### خطوات التثبيت

1. **استنساخ المشروع**
   ```bash
   git clone <repository-url>
   cd PetrolPump-Management-System-main/Project
   ```

2. **إنشاء البيئة الافتراضية**
   ```bash
   python -m venv venv
   source venv/bin/activate  # على Linux/Mac
   # أو
   venv\Scripts\activate     # على Windows
   ```

3. **تثبيت المتطلبات**
   ```bash
   pip install -r requirements.txt
   ```

4. **إعداد قاعدة البيانات**
   ```bash
   # تشغيل سكريبت إنشاء قاعدة البيانات
   python Create_database.py
   python create_enhanced_db_complete.py
   ```

5. **تشغيل التطبيق**
   ```bash
   streamlit run main_app.py
   ```

## 🔐 المصادقة والصلاحيات

### أنواع المستخدمين

- **المدير (Admin)**: وصول كامل لجميع الميزات
- **المالك (Owner)**: وصول كامل لجميع الميزات
- **الموظف (Employee)**: وصول محدود للوظائف الأساسية

### بيانات تسجيل الدخول الافتراضية

- **المدير**: `admin` / `admin123`
- **المالك**: يتم إنشاؤه من خلال قاعدة البيانات
- **الموظف**: يتم إنشاؤه من خلال قاعدة البيانات

## 📊 الميزات الأساسية

### 1. لوحة التحكم
- إحصائيات سريعة للمبيعات والمخزون
- تنبيهات المخزون المنخفض
- مؤشرات الأداء الرئيسية

### 2. الإدارة
- إدارة المحطات والمضخات والخزانات
- إدارة الموظفين والمناوبات
- إدارة أنواع الوقود والأسعار

### 3. المحاسبة
- إدارة الفواتير والمبيعات
- سندات القبض والصرف
- القيود اليومية والتقارير المالية

### 4. التقارير
- تقارير المبيعات والأرباح
- تقارير المخزون والاستهلاك
- تقارير أداء الموظفين

### 5. مراقبة الاستشعار
- قراءات الخزانات والمضخات
- التنبيهات والإنذارات
- التكامل مع أجهزة الاستشعار

## 🔧 الإعدادات المتقدمة

### متغيرات البيئة

```bash
# قاعدة البيانات
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=Petrolpump_Management_Enhanced

# الاستشعار
PTS2_API_URL=https://api.pts2-sensor.com/v1/readings
PTS2_API_KEY=your_pts2_key
ATG_API_URL=https://api.atg-sensor.com/v1/levels
ATG_API_KEY=your_atg_key

# النظام
DEBUG=false
LOG_LEVEL=INFO
```

### إعدادات الأتمتة

- **فترة التسوية التلقائية**: 7.5 ساعات
- **فترة قراءة الاستشعار**: 30 دقيقة
- **فترة النسخ الاحتياطي**: 24 ساعة

## 🧪 الاختبارات

### تشغيل الاختبارات

```bash
# تشغيل جميع الاختبارات
python scripts/run_tests.py

# تشغيل اختبارات محددة
python -m unittest tests.test_database
python -m unittest tests.test_auth
```

### كتابة اختبارات جديدة

```python
import unittest
from core.your_module import YourClass

class TestYourClass(unittest.TestCase):
    def test_your_function(self):
        # كتابة الاختبار هنا
        pass
```

## 📚 واجهات برمجة التطبيقات

### API الاستشعار

#### PTS2 Sensor API
```python
from core.sensor_api import get_sensor_api

api = get_sensor_api()
reading = api.get_sensor_reading('PTS2', 'sensor_id')
```

#### ATG Sensor API
```python
reading = api.get_sensor_reading('ATG', 'sensor_id')
```

### API قاعدة البيانات

```python
from core.database_enhanced import (
    get_all_stations,
    get_all_fuel_types,
    add_fuel_tank,
    # ... وغيرها من الوظائف
)

stations = get_all_stations()
fuel_types = get_all_fuel_types()
```

## 🔒 الأمان

### إجراءات الأمان المطبقة

1. **تشفير كلمات المرور**: استخدام خوارزميات آمنة
2. **منع الحقن SQL**: استخدام parameterized queries
3. **XSS Protection**: تقليل استخدام `unsafe_allow_html`
4. **Rate Limiting**: تحديد عدد محاولات تسجيل الدخول
5. **Session Management**: إدارة آمنة للجلسات

### أفضل الممارسات

- عدم تخزين كلمات المرور كنص واضح
- استخدام HTTPS في الإنتاج
- تحديث التبعيات بانتظام
- مراجعة السجلات بانتظام

## 🚀 النشر

### متطلبات الإنتاج

- خادم مع Python 3.8+
- خادم MySQL
- شهادة SSL لـ HTTPS
- نظام نسخ احتياطي

### خطوات النشر

1. إعداد الخادم والقاعدة
2. نسخ الملفات وتثبيت المتطلبات
3. إعداد متغيرات البيئة
4. تشغيل التطبيق مع Gunicorn أو uWSGI
5. إعداد Nginx كـ reverse proxy

## 📞 الدعم والمساعدة

### المسائل الشائعة

1. **مشكلة الاتصال بقاعدة البيانات**
   - تأكد من صحة إعدادات الاتصال
   - تحقق من تشغيل خدمة MySQL

2. **مشكلة في الاستشعار**
   - تحقق من صحة مفاتيح API
   - تأكد من اتصال الشبكة

3. **مشاكل الأداء**
   - تحسين استعلامات قاعدة البيانات
   - إضافة فهرسة للجداول الكبيرة

### سجلات النظام

- السجلات محفوظة في `api_service.log`
- مستويات السجل: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 📈 التطوير المستقبلي

### الميزات المخططة

- [ ] تطبيق جوال
- [ ] تقارير متقدمة مع الذكاء الاصطناعي
- [ ] تكامل مع أنظمة إدارة المخزون الخارجية
- [ ] دعم متعدد العملات
- [ ] واجهة برمجة تطبيقات REST API

### التحسينات المقترحة

- تحسين الأداء للقواعد الكبيرة
- إضافة المزيد من الاختبارات
- تحسين واجهة المستخدم
- دعم اللغات المتعددة

---

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT. راجع ملف `LICENSE` للمزيد من التفاصيل.

## 👥 المساهمون

- [اسم المطور] - المطور الرئيسي
- [اسماء المساهمين الآخرين]

## 📞 التواصل

للأسئلة والدعم، يرجى التواصل عبر:
- البريد الإلكتروني: support@example.com
- GitHub Issues: [رابط المشروع]