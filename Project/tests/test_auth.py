"""
اختبارات المصادقة - Authentication Tests
اختبارات وظائف المصادقة والتحقق من الصلاحيات
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# إضافة مسار المشروع إلى sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auth_manager import AuthManager


class TestAuthManager(unittest.TestCase):
    """اختبارات مدير المصادقة"""

    def setUp(self):
        """إعداد البيانات للاختبارات"""
        self.auth_mgr = AuthManager()

    def test_init_session_state(self):
        """اختبار تهيئة متغيرات الجلسة"""
        with patch('streamlit.session_state', {}) as mock_session:
            self.auth_mgr.init_session_state()

            # التحقق من تهيئة المتغيرات
            expected_keys = ['logged_in', 'user_type', 'username', 'permissions', 'login_attempts', 'locked_until']
            for key in expected_keys:
                self.assertIn(key, mock_session)

    @patch('core.auth_manager.get_connection')
    def test_authenticate_admin_success(self, mock_get_conn):
        """اختبار مصادقة المدير بنجاح"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        result = self.auth_mgr.authenticate_user("admin", "admin123")

        self.assertEqual(result, ("Admin", ["ALL"]))

    @patch('core.auth_manager.get_connection')
    def test_authenticate_owner_success(self, mock_get_conn):
        """اختبار مصادقة المالك بنجاح"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ('OWN001', 'مالك تجريبي', '0551234567', 'owner@test.com', '2024-01-01', 'ذكر', 'العنوان', 100.0, True, '2024-01-01')
        mock_get_conn.return_value = mock_conn

        result = self.auth_mgr.authenticate_user("مالك تجريبي", "0551234567")

        self.assertEqual(result, ("Owner", ["ALL"]))

    @patch('core.auth_manager.get_connection')
    def test_authenticate_employee_success(self, mock_get_conn):
        """اختبار مصادقة الموظف بنجاح"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ('EMP001', 'ST001', 'موظف تجريبي', 'ذكر', 'موظف', '1990-01-01', 5000.0, 'العنوان', 'emp@test.com', '0551234567', None, '2024-01-01', True, '2024-01-01')
        mock_get_conn.return_value = mock_conn

        result = self.auth_mgr.authenticate_user("موظف تجريبي", "EMP001")

        self.assertEqual(result, ("Employee", ['dashboard', 'management', 'reports', 'sensor_monitoring', 'accounting']))

    @patch('core.auth_manager.get_connection')
    def test_authenticate_invalid_credentials(self, mock_get_conn):
        """اختبار مصادقة بيانات غير صحيحة"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_get_conn.return_value = mock_conn

        result = self.auth_mgr.authenticate_user("invalid", "invalid")

        self.assertEqual(result, (None, []))

    def test_check_permission_admin(self):
        """اختبار فحص صلاحيات المدير"""
        result = self.auth_mgr.check_permission("Admin", "any_permission")
        self.assertTrue(result)

    def test_check_permission_owner(self):
        """اختبار فحص صلاحيات المالك"""
        result = self.auth_mgr.check_permission("Owner", "any_permission")
        self.assertTrue(result)

    def test_check_permission_employee_valid(self):
        """اختبار فحص صلاحيات الموظف الصحيحة"""
        result = self.auth_mgr.check_permission("Employee", "dashboard")
        self.assertTrue(result)

    def test_check_permission_employee_invalid(self):
        """اختبار فحص صلاحيات الموظف غير الصحيحة"""
        result = self.auth_mgr.check_permission("Employee", "admin_only")
        self.assertFalse(result)

    def test_check_account_lock_not_locked(self):
        """اختبار فحص الحساب غير المقفل"""
        with patch('streamlit.session_state', {'locked_until': None}):
            result = self.auth_mgr.check_account_lock()
            self.assertFalse(result)

    @patch('datetime.datetime')
    def test_check_account_lock_locked(self, mock_datetime):
        """اختبار فحص الحساب المقفل"""
        mock_now = MagicMock()
        mock_locked_time = MagicMock()
        mock_now.__lt__ = MagicMock(return_value=True)
        mock_datetime.now.return_value = mock_now

        with patch('streamlit.session_state', {'locked_until': mock_locked_time}):
            result = self.auth_mgr.check_account_lock()
            self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()