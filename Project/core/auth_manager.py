"""
مدير المصادقة - Authentication Manager
يحتوي على منطق المصادقة والتحقق من الصلاحيات
"""

import streamlit as st
import datetime
# from passlib.hash import bcrypt as passlib_bcrypt  # تعطيل مؤقتاً بسبب مشكلة المساحة
from typing import Optional, Tuple, List
from .database_enhanced import get_connection
from .app_config import AUTH_CONFIG, get_user_permissions


class AuthManager:
    """مدير المصادقة والصلاحيات"""

    def __init__(self):
        self.max_attempts = AUTH_CONFIG["max_login_attempts"]
        self.lockout_duration = AUTH_CONFIG["lockout_duration_minutes"]

    def init_session_state(self):
        """تهيئة متغيرات حالة الجلسة"""
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'user_type' not in st.session_state:
            st.session_state.user_type = None
        if 'username' not in st.session_state:
            st.session_state.username = ''
        if 'permissions' not in st.session_state:
            st.session_state.permissions = []
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0
        if 'locked_until' not in st.session_state:
            st.session_state.locked_until = None

    def check_account_lock(self) -> bool:
        """فحص ما إذا كان الحساب مقفلاً"""
        now = datetime.datetime.now()
        if st.session_state.locked_until and now < st.session_state.locked_until:
            return True
        return False

    def authenticate_user(self, username: str, password: str) -> Tuple[Optional[str], List[str]]:
        """مصادقة بيانات المستخدم"""
        try:
            # فحص بيانات المدير أولاً (لا يحتاج قاعدة بيانات)
            if username == "admin" and password == "admin123":
                return "Admin", ["ALL"]

            # محاولة الاتصال بقاعدة البيانات
            conn = get_connection()
            if not conn:
                # إذا فشل الاتصال، سمح فقط بالدخول كمدير
                if username == "admin" and password == "admin123":
                    return "Admin", ["ALL"]
                return None, []

            with conn:
                c = conn.cursor()

                # فحص بيانات المالك
                try:
                    c.execute("SELECT Contact_NO, hashed_password FROM Owners WHERE Owner_Name=%s", (username,))
                    owner = c.fetchone()
                    if owner:
                        contact_no = owner[0] if owner else None
                        hashed = owner[1] if len(owner) > 1 else None
                        if password == contact_no:  # استخدام التحقق البسيط
                            return "Owner", ["ALL"]
                except Exception as e:
                    print(f"خطأ في فحص المالك: {e}")

                # فحص بيانات الموظف
                try:
                    c.execute("SELECT Employee_ID, hashed_password FROM Employees WHERE Emp_Name=%s", (username,))
                    emp = c.fetchone()
                    if emp:
                        emp_id = emp[0] if emp else None
                        hashed_emp = emp[1] if len(emp) > 1 else None
                        if password == emp_id:  # استخدام التحقق البسيط
                            permissions = get_user_permissions("Employee")
                            return "Employee", permissions
                except Exception as e:
                    print(f"خطأ في فحص الموظف: {e}")

        except Exception as e:
            print(f"خطأ عام في المصادقة: {e}")
            # في حالة الخطأ، سمح فقط بالدخول كمدير
            if username == "admin" and password == "admin123":
                return "Admin", ["ALL"]

        return None, []

    def handle_login(self, username: str, password: str) -> Tuple[bool, str]:
        """معالجة عملية تسجيل الدخول"""
        user_type, permissions = self.authenticate_user(username, password)

        if user_type:
            st.session_state.logged_in = True
            st.session_state.user_type = user_type
            st.session_state.username = username
            st.session_state.permissions = permissions
            st.session_state.login_attempts = 0
            st.session_state.locked_until = None
            return True, user_type
        else:
            st.session_state.login_attempts += 1
            if st.session_state.login_attempts >= self.max_attempts:
                st.session_state.locked_until = datetime.datetime.now() + datetime.timedelta(minutes=self.lockout_duration)
                return False, f"تم قفل الحساب مؤقتاً لمدة {self.lockout_duration} دقيقة بسبب تكرار المحاولات الخاطئة."
            return False, f"بيانات الدخول غير صحيحة! (محاولة {st.session_state.login_attempts}/{self.max_attempts})"

    def check_permission(self, user_type: str, required_permission: str) -> bool:
        """فحص ما إذا كان المستخدم لديه الصلاحية المطلوبة"""
        # Admin و Owner لديهما وصول كامل
        if user_type in ['Admin', 'Owner']:
            return True

        permissions = get_user_permissions(user_type)
        return required_permission in permissions

    def logout(self):
        """تسجيل الخروج"""
        # مسح جميع متغيرات الجلسة
        keys_to_clear = ['logged_in', 'user_type', 'username', 'permissions',
                        'login_attempts', 'locked_until', 'current_page']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

    def get_current_user_info(self) -> dict:
        """الحصول على معلومات المستخدم الحالي"""
        return {
            'logged_in': st.session_state.get('logged_in', False),
            'user_type': st.session_state.get('user_type', None),
            'username': st.session_state.get('username', ''),
            'permissions': st.session_state.get('permissions', [])
        }


# إنشاء instance عام للمدير
auth_manager = AuthManager()


def get_auth_manager() -> AuthManager:
    """الحصول على instance المدير"""
    return auth_manager