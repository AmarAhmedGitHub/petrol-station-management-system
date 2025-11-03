"""
اختبارات قاعدة البيانات - Database Tests
اختبارات أساسية للوظائف الأساسية في قاعدة البيانات
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# إضافة مسار المشروع إلى sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_enhanced import get_connection, get_all_stations, get_all_fuel_types


class TestDatabaseConnection(unittest.TestCase):
    """اختبارات الاتصال بقاعدة البيانات"""

    @patch('core.database_enhanced.pymysql.connect')
    def test_get_connection_success(self, mock_connect):
        """اختبار نجاح الاتصال بقاعدة البيانات"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        result = get_connection()

        self.assertEqual(result, mock_conn)
        mock_connect.assert_called_once()

    @patch('core.database_enhanced.pymysql.connect')
    def test_get_connection_failure(self, mock_connect):
        """اختبار فشل الاتصال بقاعدة البيانات"""
        mock_connect.side_effect = Exception("Connection failed")

        result = get_connection()

        self.assertIsNone(result)


class TestDatabaseQueries(unittest.TestCase):
    """اختبارات استعلامات قاعدة البيانات"""

    def setUp(self):
        """إعداد البيانات للاختبارات"""
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    @patch('core.database_enhanced.get_connection')
    def test_get_all_stations_success(self, mock_get_conn):
        """اختبار استرجاع جميع المحطات بنجاح"""
        mock_get_conn.return_value = self.mock_conn
        self.mock_cursor.fetchall.return_value = [
            ('ST001', 'محطة الرياض', 'شركة الرياض', 'REG001', 2000, 'الرياض', 'الرياض', 'شارع الملك', '0551234567', 'EMP001', 5, 3, True, '2024-01-01')
        ]

        result = get_all_stations()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 'ST001')

    @patch('core.database_enhanced.get_connection')
    def test_get_all_fuel_types_success(self, mock_get_conn):
        """اختبار استرجاع جميع أنواع الوقود بنجاح"""
        mock_get_conn.return_value = self.mock_conn
        self.mock_cursor.fetchall.return_value = [
            ('FUEL001', 'بنزين 95', 'بنزين عادي 95 أوكتان', 8.50, True, '2024-01-01')
        ]

        result = get_all_fuel_types()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 'FUEL001')


class TestDatabaseErrorHandling(unittest.TestCase):
    """اختبارات معالجة الأخطاء في قاعدة البيانات"""

    @patch('core.database_enhanced.get_connection')
    def test_get_all_stations_connection_error(self, mock_get_conn):
        """اختبار معالجة خطأ الاتصال عند استرجاع المحطات"""
        mock_get_conn.return_value = None

        result = get_all_stations()

        self.assertEqual(result, [])

    @patch('core.database_enhanced.get_connection')
    def test_get_all_fuel_types_query_error(self, mock_get_conn):
        """اختبار معالجة خطأ الاستعلام عند استرجاع أنواع الوقود"""
        mock_get_conn.return_value = self.mock_conn = MagicMock()
        mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Query failed")

        result = get_all_fuel_types()

        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()