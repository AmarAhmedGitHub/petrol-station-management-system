"""
مسار الصفحات - Page Router
يحتوي على منطق توجيه الصفحات وإدارة التنقل
"""

import streamlit as st
from typing import Dict, Tuple, Optional
from .app_config import get_available_pages_for_user


class PageRouter:
    """مدير توجيه الصفحات"""

    def __init__(self):
        self.page_routes = {}
        self._register_routes()

    def _register_routes(self):
        """تسجيل جميع routes المتاحة"""
        # استيراد الصفحات هنا لتجنب circular imports
        from pages.dashboard.main_dashboard import main as dashboard_main
        from pages.management.main_management_enhanced import main as management_main
        from pages.management.hardware_management import main as hardware_main
        from pages.management.shift_management import main as shift_main
        from pages.accounting.main_accounting import main as accounting_main
        from pages.reports.main_reports_fixed import main as reports_main
        from pages.sensor_monitoring import main as sensor_main

        # محاولة استيراد صفحة واجهة النظام
        try:
            from pages.system_interface import main as system_main
        except ImportError:
            system_main = None

        self.page_routes = {
            'dashboard': dashboard_main,
            'management': management_main,
            'hardware_management': hardware_main,
            'shift_management': shift_main,
            'accounting': accounting_main,
            'reports': reports_main,
            'sensor_monitoring': sensor_main,
            'system_interface': lambda: system_main() if system_main else st.info("🚧 واجهة النظام غير متاحة حالياً")
        }

    def get_available_pages(self, user_type: str) -> Dict[str, Tuple[str, str]]:
        """الحصول على الصفحات المتاحة لنوع المستخدم"""
        return get_available_pages_for_user(user_type)

    def route_to_page(self, page_id: str):
        """توجيه إلى الصفحة المطلوبة"""
        page_function = self.page_routes.get(page_id, self.page_routes['dashboard'])

        try:
            if page_id == 'system_interface':
                # معالجة خاصة لصفحة واجهة النظام
                if 'system_interface' in self.page_routes:
                    self.page_routes['system_interface']()
                else:
                    st.info("🚧 واجهة النظام غير متاحة حالياً")
            else:
                page_function()
        except Exception as e:
            st.error(f"خطأ في تحميل الصفحة: {e}")
            st.info("🔄 جاري العودة إلى لوحة التحكم...")
            self.page_routes['dashboard']()

    def validate_page_access(self, user_type: str, page_id: str) -> bool:
        """التحقق من صلاحية الوصول للصفحة"""
        available_pages = self.get_available_pages(user_type)
        return page_id in available_pages

    def get_default_page(self, user_type: str) -> str:
        """الحصول على الصفحة الافتراضية لنوع المستخدم"""
        available_pages = self.get_available_pages(user_type)
        if available_pages:
            return list(available_pages.keys())[0]
        return 'dashboard'


# إنشاء instance عام للراوتر
page_router = PageRouter()


def get_page_router() -> PageRouter:
    """الحصول على instance الراوتر"""
    return page_router