"""
نظام Audit Trail للتغييرات الحساسة - Petrol Pump Management System
يوفر هذا النظام تتبع شامل لجميع التغييرات في قاعدة البيانات
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from database import get_connection
import streamlit as st

# إعداد نظام التسجيل
logging.basicConfig(
    filename='audit_trail.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class AuditTrail:
    """نظام تتبع التغييرات"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # الجداول التي تحتاج تتبع
        self.audited_tables = {
            'Employee': ['Employee_ID', 'Emp_Name', 'Salary', 'Emp_Address', 'Email_ID'],
            'Owners': ['Owner_Name', 'Contact_NO', 'Address'],
            'Customer': ['Customer_Code', 'C_Name', 'Phone_No', 'Email_ID', 'City'],
            'Invoice': ['Invoice_No', 'Total_Price', 'Customer_Code'],
            'Tanker': ['Tanker_ID', 'Fuel_Price', 'Capacity'],
            'FuelTank': ['FuelTank_ID', 'Current_Amount'],
            'EmployeePermissions': ['Employee_ID', 'Permission']
        }

    def log_change(self, table_name: str, record_id: str, action_type: str,
                   old_values: Optional[Dict[str, Any]] = None,
                   new_values: Optional[Dict[str, Any]] = None,
                   user_id: Optional[str] = None,
                   user_type: str = 'System',
                   ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None) -> bool:
        """
        تسجيل تغيير في قاعدة البيانات

        Args:
            table_name: اسم الجدول
            record_id: معرف السجل
            action_type: نوع العملية (INSERT, UPDATE, DELETE)
            old_values: القيم القديمة
            new_values: القيم الجديدة
            user_id: معرف المستخدم
            user_type: نوع المستخدم
            ip_address: عنوان IP
            user_agent: معلومات المتصفح

        Returns:
            bool: نجح/فشل
        """
        try:
            conn = get_connection()
            if not conn:
                return False

            c = conn.cursor()

            # تحويل القيم إلى JSON
            old_json = json.dumps(old_values, ensure_ascii=False) if old_values else None
            new_json = json.dumps(new_values, ensure_ascii=False) if new_values else None

            # تسجيل العملية
            c.execute("""
                INSERT INTO AuditTrail
                (Table_Name, Record_ID, Action_Type, Old_Values, New_Values,
                 User_ID, User_Type, Action_Date, IP_Address, User_Agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (table_name, record_id, action_type, old_json, new_json,
                  user_id, user_type, datetime.now(), ip_address, user_agent))

            conn.commit()
            conn.close()

            self.logger.info(f"Audit logged: {action_type} on {table_name}.{record_id} by {user_type}:{user_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to log audit: {str(e)}")
            return False

    def get_audit_history(self, table_name: Optional[str] = None,
                         record_id: Optional[str] = None,
                         user_id: Optional[str] = None,
                         action_type: Optional[str] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """
        الحصول على سجل التغييرات

        Args:
            table_name: فلترة حسب الجدول
            record_id: فلترة حسب معرف السجل
            user_id: فلترة حسب المستخدم
            action_type: فلترة حسب نوع العملية
            start_date: تاريخ البداية
            end_date: تاريخ النهاية
            limit: عدد السجلات المراد إرجاعها

        Returns:
            List[Dict]: قائمة بالتغييرات
        """
        try:
            conn = get_connection()
            if not conn:
                return []

            c = conn.cursor()

            query = """
                SELECT Audit_ID, Table_Name, Record_ID, Action_Type,
                       Old_Values, New_Values, User_ID, User_Type,
                       Action_Date, IP_Address, User_Agent
                FROM AuditTrail
                WHERE 1=1
            """
            params = []

            if table_name:
                query += " AND Table_Name = %s"
                params.append(table_name)

            if record_id:
                query += " AND Record_ID = %s"
                params.append(record_id)

            if user_id:
                query += " AND User_ID = %s"
                params.append(user_id)

            if action_type:
                query += " AND Action_Type = %s"
                params.append(action_type)

            if start_date:
                query += " AND Action_Date >= %s"
                params.append(start_date)

            if end_date:
                query += " AND Action_Date <= %s"
                params.append(end_date)

            query += " ORDER BY Action_Date DESC LIMIT %s"
            params.append(limit)

            c.execute(query, params)
            results = c.fetchall()
            conn.close()

            audit_history = []
            for row in results:
                audit_history.append({
                    'audit_id': row[0],
                    'table_name': row[1],
                    'record_id': row[2],
                    'action_type': row[3],
                    'old_values': json.loads(row[4]) if row[4] else None,
                    'new_values': json.loads(row[5]) if row[5] else None,
                    'user_id': row[6],
                    'user_type': row[7],
                    'action_date': row[8],
                    'ip_address': row[9],
                    'user_agent': row[10]
                })

            return audit_history

        except Exception as e:
            self.logger.error(f"Error retrieving audit history: {str(e)}")
            return []

    def get_table_changes_summary(self, table_name: str,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> Dict[str, int]:
        """
        الحصول على ملخص التغييرات في جدول معين

        Args:
            table_name: اسم الجدول
            start_date: تاريخ البداية
            end_date: تاريخ النهاية

        Returns:
            Dict[str, int]: ملخص التغييرات
        """
        try:
            conn = get_connection()
            if not conn:
                return {}

            c = conn.cursor()

            query = """
                SELECT Action_Type, COUNT(*) as Count
                FROM AuditTrail
                WHERE Table_Name = %s
            """
            params = [table_name]

            if start_date:
                query += " AND Action_Date >= %s"
                params.append(start_date)

            if end_date:
                query += " AND Action_Date <= %s"
                params.append(end_date)

            query += " GROUP BY Action_Type"

            c.execute(query, params)
            results = c.fetchall()
            conn.close()

            summary = {'INSERT': 0, 'UPDATE': 0, 'DELETE': 0}
            for row in results:
                summary[row[0]] = row[1]

            return summary

        except Exception as e:
            self.logger.error(f"Error getting table changes summary: {str(e)}")
            return {}

    def get_user_activity(self, user_id: str,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        الحصول على نشاط مستخدم معين

        Args:
            user_id: معرف المستخدم
            start_date: تاريخ البداية
            end_date: تاريخ النهاية

        Returns:
            List[Dict]: قائمة بالأنشطة
        """
        return self.get_audit_history(user_id=user_id, start_date=start_date, end_date=end_date)

    def detect_suspicious_activity(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        كشف الأنشطة المشبوهة

        Args:
            hours: عدد الساعات الماضية للبحث

        Returns:
            List[Dict]: قائمة بالأنشطة المشبوهة
        """
        try:
            from datetime import timedelta
            start_date = datetime.now() - timedelta(hours=hours)

            # البحث عن أنشطة مشبوهة
            suspicious_patterns = [
                # محاولات حذف متعددة
                "DELETE",
                # تغييرات في الرواتب
                "UPDATE.*Salary",
                # تغييرات في الأسعار
                "UPDATE.*Fuel_Price"
            ]

            suspicious_activities = []

            for pattern in suspicious_patterns:
                if "DELETE" in pattern:
                    activities = self.get_audit_history(
                        action_type="DELETE",
                        start_date=start_date
                    )
                    suspicious_activities.extend(activities)
                elif "Salary" in pattern:
                    # البحث عن تغييرات في الرواتب
                    activities = self.get_audit_history(
                        table_name="Employee",
                        action_type="UPDATE",
                        start_date=start_date
                    )
                    for activity in activities:
                        if activity['new_values'] and 'Salary' in str(activity['new_values']):
                            suspicious_activities.append(activity)
                elif "Fuel_Price" in pattern:
                    # البحث عن تغييرات في أسعار الوقود
                    activities = self.get_audit_history(
                        table_name="Tanker",
                        action_type="UPDATE",
                        start_date=start_date
                    )
                    for activity in activities:
                        if activity['new_values'] and 'Fuel_Price' in str(activity['new_values']):
                            suspicious_activities.append(activity)

            return suspicious_activities

        except Exception as e:
            self.logger.error(f"Error detecting suspicious activity: {str(e)}")
            return []

    def get_audit_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        الحصول على إحصائيات التدقيق

        Args:
            days: عدد الأيام الماضية

        Returns:
            Dict: الإحصائيات
        """
        try:
            from datetime import timedelta
            start_date = datetime.now() - timedelta(days=days)

            conn = get_connection()
            if not conn:
                return {}

            c = conn.cursor()

            # إجمالي العمليات
            c.execute("SELECT COUNT(*) FROM AuditTrail WHERE Action_Date >= %s", (start_date,))
            total_operations = c.fetchone()[0]

            # العمليات حسب النوع
            c.execute("""
                SELECT Action_Type, COUNT(*) as Count
                FROM AuditTrail
                WHERE Action_Date >= %s
                GROUP BY Action_Type
            """, (start_date,))
            operations_by_type = dict(c.fetchall())

            # العمليات حسب المستخدم
            c.execute("""
                SELECT User_Type, COUNT(*) as Count
                FROM AuditTrail
                WHERE Action_Date >= %s
                GROUP BY User_Type
            """, (start_date,))
            operations_by_user_type = dict(c.fetchall())

            # الجداول الأكثر تغييراً
            c.execute("""
                SELECT Table_Name, COUNT(*) as Count
                FROM AuditTrail
                WHERE Action_Date >= %s
                GROUP BY Table_Name
                ORDER BY Count DESC
                LIMIT 10
            """, (start_date,))
            tables_by_changes = dict(c.fetchall())

            conn.close()

            return {
                'total_operations': total_operations,
                'operations_by_type': operations_by_type,
                'operations_by_user_type': operations_by_user_type,
                'tables_by_changes': tables_by_changes,
                'period_days': days
            }

        except Exception as e:
            self.logger.error(f"Error getting audit stats: {str(e)}")
            return {}

# إنشاء instance عالمي
audit_trail = AuditTrail()

# دوال مساعدة للاستخدام في Streamlit
def log_user_action(table_name: str, record_id: str, action_type: str,
                   old_values: Optional[Dict[str, Any]] = None,
                   new_values: Optional[Dict[str, Any]] = None):
    """تسجيل عملية المستخدم الحالي"""
    user_id = st.session_state.get('username')
    user_type = st.session_state.get('user_type', 'System')

    # الحصول على IP (محاكاة)
    ip_address = "127.0.0.1"  # في بيئة حقيقية، احصل من الطلب
    user_agent = "Streamlit App"

    return audit_trail.log_change(
        table_name=table_name,
        record_id=record_id,
        action_type=action_type,
        old_values=old_values,
        new_values=new_values,
        user_id=user_id,
        user_type=user_type,
        ip_address=ip_address,
        user_agent=user_agent
    )

def display_audit_history(filters: Optional[Dict[str, Any]] = None):
    """عرض سجل التغييرات في Streamlit"""
    st.subheader("📋 سجل التغييرات (Audit Trail)")

    # فلاتر البحث
    col1, col2, col3 = st.columns(3)

    with col1:
        table_filter = st.selectbox(
            "الجدول:",
            ["الكل", "Employee", "Owners", "Customer", "Invoice", "Tanker", "FuelTank"],
            key="audit_table_filter"
        )

    with col2:
        action_filter = st.selectbox(
            "نوع العملية:",
            ["الكل", "INSERT", "UPDATE", "DELETE"],
            key="audit_action_filter"
        )

    with col3:
        days_filter = st.selectbox(
            "الفترة:",
            [7, 30, 90, 365],
            key="audit_days_filter"
        )

    # تطبيق الفلاتر
    from datetime import timedelta
    start_date = datetime.now() - timedelta(days=days_filter)

    table_name = None if table_filter == "الكل" else table_filter
    action_type = None if action_filter == "الكل" else action_filter

    # الحصول على السجل
    audit_history = audit_trail.get_audit_history(
        table_name=table_name,
        action_type=action_type,
        start_date=start_date,
        limit=50
    )

    if not audit_history:
        st.info("لا توجد تغييرات في السجل لهذه الفلاتر")
        return

    # عرض النتائج
    for entry in audit_history:
        with st.expander(f"{entry['action_type']} - {entry['table_name']}.{entry['record_id']} - {entry['action_date']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**المستخدم:** {entry['user_type']} - {entry['user_id'] or 'غير محدد'}")
                st.write(f"**التاريخ:** {entry['action_date']}")

            with col2:
                st.write(f"**عنوان IP:** {entry['ip_address'] or 'غير محدد'}")

            if entry['old_values']:
                st.write("**القيم القديمة:**")
                st.json(entry['old_values'])

            if entry['new_values']:
                st.write("**القيم الجديدة:**")
                st.json(entry['new_values'])

def display_audit_stats():
    """عرض إحصائيات التدقيق في Streamlit"""
    st.subheader("📊 إحصائيات التدقيق")

    stats = audit_trail.get_audit_stats(days=30)

    if not stats:
        st.warning("لا توجد إحصائيات متاحة")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("إجمالي العمليات", stats.get('total_operations', 0))

    with col2:
        inserts = stats.get('operations_by_type', {}).get('INSERT', 0)
        st.metric("عمليات الإضافة", inserts)

    with col3:
        updates = stats.get('operations_by_type', {}).get('UPDATE', 0)
        st.metric("عمليات التعديل", updates)

    with col4:
        deletes = stats.get('operations_by_type', {}).get('DELETE', 0)
        st.metric("عمليات الحذف", deletes)

    # توزيع حسب نوع المستخدم
    st.subheader("توزيع العمليات حسب نوع المستخدم")
    user_stats = stats.get('operations_by_user_type', {})
    if user_stats:
        user_data = []
        for user_type, count in user_stats.items():
            user_data.append({"نوع المستخدم": user_type, "عدد العمليات": count})

        import pandas as pd
        df = pd.DataFrame(user_data)
        st.bar_chart(df.set_index("نوع المستخدم"))
    else:
        st.info("لا توجد بيانات")

def display_suspicious_activity():
    """عرض الأنشطة المشبوهة في Streamlit"""
    st.subheader("🚨 الأنشطة المشبوهة")

    suspicious = audit_trail.detect_suspicious_activity(hours=24)

    if not suspicious:
        st.success("لا توجد أنشطة مشبوهة في الـ24 ساعة الماضية")
        return

    st.warning(f"تم اكتشاف {len(suspicious)} نشاط مشبوه")

    for activity in suspicious:
        with st.expander(f"⚠️ {activity['action_type']} - {activity['table_name']}.{activity['record_id']}"):
            st.write(f"**المستخدم:** {activity['user_type']} - {activity['user_id']}")
            st.write(f"**التاريخ:** {activity['action_date']}")
            st.write(f"**الجدول:** {activity['table_name']}")

            if activity['old_values']:
                st.write("**قبل التغيير:**")
                st.json(activity['old_values'])

            if activity['new_values']:
                st.write("**بعد التغيير:**")
                st.json(activity['new_values'])