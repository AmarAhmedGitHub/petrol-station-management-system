# دليل استضافة Streamlit على Hostinger - Streamlit Hosting Guide

## نظرة عامة
هذا الدليل يوضح كيفية استضافة تطبيق Streamlit لنظام إدارة محطات الوقود مباشرة على Hostinger VPS بدون استخدام Docker.

## المتطلبات
- حساب Hostinger VPS
- Python 3.8+ مثبت على الخادم
- بيانات قاعدة البيانات من Hostinger MySQL
- SSH access للخادم

## خطوات الاستضافة

### 1. تحضير الملفات المحلية
```bash
cd Project/deploy/
python streamlit_hosting.py
```
سيتم إنشاء مجلد `streamlit_hosting/` يحتوي على جميع الملفات المطلوبة.

### 2. رفع الملفات إلى Hostinger
#### الطريقة الأولى: استخدام SFTP/FTP
- ارفع محتويات مجلد `streamlit_hosting/` إلى مجلد على الخادم
- مثال: `/home/username/petrol-station/`

#### الطريقة الثانية: استخدام rsync (أفضل)
```bash
# من جهازك المحلي
rsync -avz streamlit_hosting/ username@your-hostinger-domain.com:/home/username/petrol-station/
```

### 3. إعداد البيئة على الخادم
#### الاتصال بالخادم عبر SSH
```bash
ssh username@your-hostinger-domain.com
```

#### تثبيت Python و pip
```bash
# تحقق من Python
python3 --version

# تثبيت pip إذا لم يكن موجوداً
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

#### تثبيت المتطلبات
```bash
cd /home/username/petrol-station/
pip3 install -r requirements_production.txt
```

### 4. إعداد قاعدة البيانات
#### رفع ملف قاعدة البيانات
```bash
# من مجلد deploy المحلي
scp database_hosting.sql username@your-hostinger-domain.com:/home/username/
scp setup_database_hosting.py username@your-hostinger-domain.com:/home/username/
```

#### إعداد قاعدة البيانات على الخادم
```bash
cd /home/username/
python3 setup_database_hosting.py
```

### 5. إعداد متغيرات البيئة
```bash
cd /home/username/petrol-station/

# نسخ ملف البيئة
cp .env.production .env

# تحرير الملف بالبيانات الصحيحة
nano .env
```

#### محتوى ملف .env
```env
# Database Configuration
DB_HOST=your-hostinger-mysql-host.com
DB_USER=your_database_username
DB_PASSWORD=your_secure_password
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

### 6. تشغيل التطبيق
```bash
cd /home/username/petrol-station/
python3 startup.py
```

## إعداد التشغيل التلقائي

### إنشاء خدمة Systemd
```bash
sudo nano /etc/systemd/system/petrol-station.service
```

#### محتوى ملف الخدمة
```ini
[Unit]
Description=Petrol Station Management System
After=network.target

[Service]
Type=simple
User=username
WorkingDirectory=/home/username/petrol-station
ExecStart=/usr/bin/python3 startup.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### تفعيل وتشغيل الخدمة
```bash
sudo systemctl daemon-reload
sudo systemctl enable petrol-station
sudo systemctl start petrol-station
sudo systemctl status petrol-station
```

## إعداد Nginx (اختياري للمنفذ 80)

### تثبيت Nginx
```bash
sudo apt update
sudo apt install nginx
```

### إعداد الموقع
```bash
sudo nano /etc/nginx/sites-available/petrol-station
```

#### محتوى إعداد Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support for Streamlit
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### تفعيل الموقع
```bash
sudo ln -s /etc/nginx/sites-available/petrol-station /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## إعداد SSL (اختياري)

### تثبيت Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### الحصول على شهادة SSL
```bash
sudo certbot --nginx -d your-domain.com
```

## مراقبة التطبيق

### مراجعة السجلات
```bash
# سجلات Streamlit
tail -f ~/.streamlit/logs/streamlit.log

# سجلات النظام
sudo journalctl -u petrol-station -f
```

### إعادة تشغيل التطبيق
```bash
sudo systemctl restart petrol-station
```

## استكشاف الأخطاء

### مشكلة في قاعدة البيانات
```
❌ Database connection failed
```
**الحل:** تحقق من بيانات الاتصال في ملف `.env`

### مشكلة في المنفذ
```
Port 8501 already in use
```
**الحل:** غير المنفذ في ملف `.env` أو أعد تشغيل الخادم

### مشكلة في الذاكرة
```
MemoryError
```
**الحل:** زد ذاكرة VPS أو قلل من استخدام البيانات الكبيرة

### مشكلة في التبعيات
```
ModuleNotFoundError
```
**الحل:** أعد تثبيت المتطلبات
```bash
pip3 install -r requirements_production.txt --force-reinstall
```

## الأمان

### إعداد Firewall
```bash
sudo ufw allow 8501
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### تحديث النظام بانتظام
```bash
sudo apt update && sudo apt upgrade
```

### نسخ احتياطي
```bash
# نسخ احتياطي لقاعدة البيانات
mysqldump -h your-host DB_NAME > backup_$(date +%Y%m%d).sql

# نسخ احتياطي للملفات
tar -czf backup_$(date +%Y%m%d).tar.gz /home/username/petrol-station/
```

## الأداء

### تحسين Streamlit
- استخدم `--server.headless true`
- حدد حجم الرفع الأقصى
- عطل جمع الإحصائيات

### تحسين قاعدة البيانات
- أضف فهارس للجداول الكبيرة
- قم بتحسين الاستعلامات
- استخدم اتصال مستمر

## الدعم والمساعدة

إذا واجهت مشاكل:
1. راجع سجلات النظام
2. تحقق من اتصال قاعدة البيانات
3. تأكد من تثبيت جميع المتطلبات
4. راجع إعدادات Firewall

---

**تم إنشاء هذا الدليل بواسطة نظام إدارة محطات الوقود المتقدم**
