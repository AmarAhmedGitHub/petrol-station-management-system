"""
تكوين التطبيق - Application Configuration
يحتوي على الإعدادات العامة والثوابت المستخدمة في التطبيق
"""

import os
from typing import Dict, Any

# إعدادات الصفحة الرئيسية
PAGE_CONFIG = {
    "page_title": "نظام إدارة محطات الوقود - مع الاستشعار الآلي والمحاسبة",
    "page_icon": "⛽",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# إعدادات قاعدة البيانات
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "Petrolpump_Management_Enhanced"),
    "charset": "utf8mb4"
}

# إعدادات المصادقة
AUTH_CONFIG = {
    "max_login_attempts": 5,
    "lockout_duration_minutes": 2,
    "session_timeout_hours": 8
}

# إعدادات الأتمتة
AUTOMATION_CONFIG = {
    "reconciliation_interval_hours": 7.5,
    "sensor_readings_interval_minutes": 30,
    "backup_interval_hours": 24
}

# أنواع المستخدمين وصلاحياتهم
USER_TYPES = {
    "Admin": {
        "permissions": ["ALL"],
        "description": "مدير النظام الكامل"
    },
    "Owner": {
        "permissions": ["ALL"],
        "description": "مالك المحطة"
    },
    "Employee": {
        "permissions": ["dashboard", "management", "reports", "sensor_monitoring", "accounting"],
        "description": "موظف المحطة"
    }
}

# الصفحات المتاحة في النظام
AVAILABLE_PAGES = {
    'dashboard': ('📊 لوحة التحكم', 'dashboard'),
    'management': ('⚙️ الإدارة', 'management'),
    'hardware_management': ('🔧 إدارة الأجهزة والمعدات', 'hardware_management'),
    'shift_management': ('🕐 إدارة المناوبات', 'shift_management'),
    'accounting': ('💼 المحاسبة', 'accounting'),
    'reports': ('📈 التقارير', 'reports'),
    'sensor_monitoring': ('📡 مراقبة الاستشعار', 'sensor_monitoring'),
    'system_interface': ('🔧 واجهة النظام', 'system_interface')
}

# إعدادات التصميم
DESIGN_CONFIG = {
    "theme": "light",  # light, dark, auto
    "rtl_support": True,
    "animations_enabled": True
}

# إعدادات النظام
SYSTEM_CONFIG = {
    "version": "2.0.0",
    "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "max_upload_size_mb": 10
}

def get_page_config() -> Dict[str, Any]:
    """الحصول على إعدادات الصفحة"""
    return PAGE_CONFIG.copy()

def get_db_config() -> Dict[str, Any]:
    """الحصول على إعدادات قاعدة البيانات"""
    return DB_CONFIG.copy()

def get_user_permissions(user_type: str) -> list:
    """الحصول على صلاحيات نوع المستخدم"""
    return USER_TYPES.get(user_type, {}).get("permissions", [])

def get_available_pages_for_user(user_type: str) -> Dict[str, tuple]:
    """الحصول على الصفحات المتاحة لنوع المستخدم"""
    if user_type in ['Admin', 'Owner']:
        return AVAILABLE_PAGES.copy()

    user_permissions = get_user_permissions(user_type)
    return {
        page_id: page_info
        for page_id, page_info in AVAILABLE_PAGES.items()
        if page_id in user_permissions
    }

def is_debug_mode() -> bool:
    """فحص ما إذا كان النظام في وضع التصحيح"""
    return SYSTEM_CONFIG["debug_mode"]

def get_system_version() -> str:
    """الحصول على إصدار النظام"""
    return SYSTEM_CONFIG["version"]