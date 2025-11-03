"""
نظام إدارة الصلاحيات المتقدم - Petrol Pump Management System
يوفر هذا النظام فصل واجهات حقيقي حسب الصلاحيات
"""

import logging
from typing import Dict, List, Set, Optional
from database import get_connection
import streamlit as st

# إعداد نظام التسجيل
logging.basicConfig(
    filename='permission_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class PermissionManager:
    """مدير الصلاحيات المتقدم"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # تعريف الصلاحيات المتاحة
        self.available_permissions = {
            'DASHBOARD': 'الوصول للوحة التحكم',
            'INVOICE': 'إدارة الفواتير',
            'CUSTOMER': 'إدارة العملاء',
            'EMPLOYEE': 'إدارة الموظفين',
            'OWNER': 'إدارة الملاك',
            'PETROLPUMP': 'إدارة المحطات',
            'TANKER': 'إدارة الخزانات',
            'FUEL_SUPPLY': 'إدارة توريد الوقود',
            'MAINTENANCE': 'إدارة الصيانة',
            'REPORTS': 'عرض التقارير',
            'MANAGEMENT': 'الإدارة العامة',
            'ADMIN': 'صلاحيات المدير',
            'SETTINGS': 'إعدادات النظام',
            'AUDIT': 'عرض سجل التغييرات',
            'BACKUP': 'النسخ الاحتياطي'
        }

        # الصلاحيات الافتراضية لكل نوع مستخدم
        self.default_permissions = {
            'Admin': list(self.available_permissions.keys()),
            'Owner': [
                'DASHBOARD', 'INVOICE', 'CUSTOMER', 'EMPLOYEE', 'PETROLPUMP',
                'TANKER', 'FUEL_SUPPLY', 'REPORTS', 'MANAGEMENT', 'MAINTENANCE'
            ],
            'Employee': [
                'DASHBOARD', 'INVOICE', 'CUSTOMER'
            ]
        }

        # قاموس الصلاحيات باللغة العربية
        self.permission_translations = {
            'DASHBOARD': 'لوحة التحكم',
            'INVOICE': 'الفواتير',
            'CUSTOMER': 'العملاء',
            'EMPLOYEE': 'الموظفين',
            'OWNER': 'الملاك',
            'PETROLPUMP': 'المحطات',
            'TANKER': 'الخزانات',
            'FUEL_SUPPLY': 'توريد الوقود',
            'MAINTENANCE': 'الصيانة',
            'REPORTS': 'التقارير',
            'MANAGEMENT': 'الإدارة',
            'ADMIN': 'المدير',
            'SETTINGS': 'الإعدادات',
            'AUDIT': 'سجل التغييرات',
            'BACKUP': 'النسخ الاحتياطي'
        }

    def get_user_permissions(self, user_id: str, user_type: str) -> List[str]:
        """
        الحصول على صلاحيات المستخدم

        Args:
            user_id: معرف المستخدم
            user_type: نوع المستخدم

        Returns:
            List[str]: قائمة الصلاحيات
        """
        try:
            # للمدير والمالك، إرجاع الصلاحيات الافتراضية
            if user_type in ['Admin', 'Owner']:
                return self.default_permissions.get(user_type, [])

            # للموظف، الحصول من قاعدة البيانات
            if user_type == 'Employee':
                conn = get_connection()
                if not conn:
                    return []

                c = conn.cursor()
                c.execute("SELECT Permission FROM EmployeePermissions WHERE Employee_ID = %s", (user_id,))
                permissions = [row[0] for row in c.fetchall()]
                conn.close()

                # إذا لم تكن هناك صلاحيات محددة، استخدم الافتراضية
                if not permissions:
                    permissions = self.default_permissions.get('Employee', [])

                return permissions

            return []

        except Exception as e:
            self.logger.error(f"Error getting user permissions: {str(e)}")
            return []

    def has_permission(self, user_permissions: List[str], required_permission: str) -> bool:
        """
        التحقق من وجود صلاحية معينة

        Args:
            user_permissions: صلاحيات المستخدم
            required_permission: الصلاحية المطلوبة

        Returns:
            bool: True إذا كانت الصلاحية موجودة
        """
        return required_permission in user_permissions

    def has_any_permission(self, user_permissions: List[str], required_permissions: List[str]) -> bool:
        """
        التحقق من وجود أي من الصلاحيات المطلوبة

        Args:
            user_permissions: صلاحيات المستخدم
            required_permissions: الصلاحيات المطلوبة

        Returns:
            bool: True إذا كانت أي من الصلاحيات موجودة
        """
        return any(perm in user_permissions for perm in required_permissions)

    def has_all_permissions(self, user_permissions: List[str], required_permissions: List[str]) -> bool:
        """
        التحقق من وجود جميع الصلاحيات المطلوبة

        Args:
            user_permissions: صلاحيات المستخدم
            required_permissions: الصلاحيات المطلوبة

        Returns:
            bool: True إذا كانت جميع الصلاحيات موجودة
        """
        return all(perm in user_permissions for perm in required_permissions)

    def update_employee_permissions(self, employee_id: str, permissions: List[str]) -> bool:
        """
        تحديث صلاحيات موظف

        Args:
            employee_id: معرف الموظف
            permissions: الصلاحيات الجديدة

        Returns:
            bool: نجح/فشل
        """
        try:
            conn = get_connection()
            if not conn:
                return False

            c = conn.cursor()
            conn.begin()

            # حذف الصلاحيات القديمة
            c.execute("DELETE FROM EmployeePermissions WHERE Employee_ID = %s", (employee_id,))

            # إضافة الصلاحيات الجديدة
            for permission in permissions:
                c.execute("""
                    INSERT INTO EmployeePermissions (Employee_ID, Permission)
                    VALUES (%s, %s)
                """, (employee_id, permission))

            conn.commit()
            conn.close()

            self.logger.info(f"Updated permissions for employee {employee_id}: {permissions}")
            return True

        except Exception as e:
            conn.rollback()
            conn.close()
            self.logger.error(f"Error updating employee permissions: {str(e)}")
            return False

    def get_permission_groups(self) -> Dict[str, List[str]]:
        """
        الحصول على مجموعات الصلاحيات

        Returns:
            Dict[str, List[str]]: مجموعات الصلاحيات
        """
        return {
            'الأساسية': ['DASHBOARD', 'REPORTS'],
            'إدارة المبيعات': ['INVOICE', 'CUSTOMER'],
            'إدارة الموارد البشرية': ['EMPLOYEE', 'OWNER'],
            'إدارة المخزون': ['PETROLPUMP', 'TANKER', 'FUEL_SUPPLY', 'MAINTENANCE'],
            'الإدارة العامة': ['MANAGEMENT', 'SETTINGS'],
            'النظام': ['ADMIN', 'AUDIT', 'BACKUP']
        }

    def validate_permission_assignment(self, employee_id: str, permissions: List[str]) -> Tuple[bool, str]:
        """
        التحقق من صحة تعيين الصلاحيات

        Args:
            employee_id: معرف الموظف
            permissions: الصلاحيات المراد تعيينها

        Returns:
            Tuple[bool, str]: (صحيح/خطأ, رسالة)
        """
        try:
            # التحقق من وجود الموظف
            conn = get_connection()
            if not conn:
                return False, "فشل في الاتصال بقاعدة البيانات"

            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM Employee WHERE Employee_ID = %s", (employee_id,))
            if c.fetchone()[0] == 0:
                conn.close()
                return False, f"الموظف {employee_id} غير موجود"

            # التحقق من صحة الصلاحيات
            invalid_permissions = []
            for perm in permissions:
                if perm not in self.available_permissions:
                    invalid_permissions.append(perm)

            conn.close()

            if invalid_permissions:
                return False, f"الصلاحيات التالية غير صحيحة: {', '.join(invalid_permissions)}"

            return True, "تعيين الصلاحيات صحيح"

        except Exception as e:
            self.logger.error(f"Error validating permission assignment: {str(e)}")
            return False, f"خطأ في النظام: {str(e)}"

    def get_permission_matrix(self) -> Dict[str, Dict[str, bool]]:
        """
        الحصول على مصفوفة الصلاحيات لجميع الموظفين

        Returns:
            Dict[str, Dict[str, bool]]: مصفوفة الصلاحيات
        """
        try:
            conn = get_connection()
            if not conn:
                return {}

            c = conn.cursor()

            # الحصول على جميع الموظفين
            c.execute("SELECT Employee_ID, Emp_Name FROM Employee")
            employees = c.fetchall()

            # الحصول على جميع الصلاحيات
            c.execute("SELECT Employee_ID, Permission FROM EmployeePermissions")
            permissions_data = c.fetchall()

            conn.close()

            # تنظيم البيانات
            permission_matrix = {}
            for emp_id, emp_name in employees:
                emp_permissions = [row[1] for row in permissions_data if row[0] == emp_id]
                permission_matrix[f"{emp_name} ({emp_id})"] = {
                    perm: perm in emp_permissions
                    for perm in self.available_permissions.keys()
                }

            return permission_matrix

        except Exception as e:
            self.logger.error(f"Error getting permission matrix: {str(e)}")
            return {}

# إنشاء instance عالمي
permission_manager = PermissionManager()

# دوال مساعدة للاستخدام في Streamlit
def check_permission(required_permission: str) -> bool:
    """التحقق من صلاحية المستخدم الحالي"""
    if 'user_type' not in st.session_state:
        return False

    user_permissions = permission_manager.get_user_permissions(
        st.session_state.get('username', ''),
        st.session_state.user_type
    )

    return permission_manager.has_permission(user_permissions, required_permission)

def check_any_permission(required_permissions: List[str]) -> bool:
    """التحقق من وجود أي من الصلاحيات المطلوبة"""
    if 'user_type' not in st.session_state:
        return False

    user_permissions = permission_manager.get_user_permissions(
        st.session_state.get('username', ''),
        st.session_state.user_type
    )

    return permission_manager.has_any_permission(user_permissions, required_permissions)

def require_permission(required_permission: str, message: str = "ليس لديك صلاحية للوصول لهذه الصفحة"):
    """التحقق من الصلاحية وعرض رسالة خطأ إذا لم تكن موجودة"""
    if not check_permission(required_permission):
        st.error(message)
        st.stop()

def require_any_permission(required_permissions: List[str], message: str = "ليس لديك الصلاحيات المطلوبة"):
    """التحقق من وجود أي من الصلاحيات المطلوبة"""
    if not check_any_permission(required_permissions):
        st.error(message)
        st.stop()

def display_permission_manager():
    """عرض واجهة إدارة الصلاحيات في Streamlit"""
    st.subheader("🔐 إدارة صلاحيات الموظفين")

    # التحقق من صلاحية المدير
    require_permission('ADMIN', "يجب أن تكون مديراً للوصول لإدارة الصلاحيات")

    # الحصول على قائمة الموظفين
    try:
        conn = get_connection()
        if not conn:
            st.error("فشل في الاتصال بقاعدة البيانات")
            return

        c = conn.cursor()
        c.execute("SELECT Employee_ID, Emp_Name FROM Employee ORDER BY Emp_Name")
        employees = c.fetchall()
        conn.close()

        if not employees:
            st.info("لا يوجد موظفون مسجلون")
            return

        # اختيار الموظف
        emp_options = {f"{name} ({emp_id})": emp_id for emp_id, name in employees}
        selected_emp = st.selectbox(
            "اختر الموظف:",
            list(emp_options.keys()),
            key="perm_emp_select"
        )

        emp_id = emp_options[selected_emp]

        # الحصول على الصلاحيات الحالية
        current_permissions = permission_manager.get_user_permissions(emp_id, 'Employee')

        st.subheader(f"صلاحيات {selected_emp}")

        # عرض الصلاحيات في مجموعات
        permission_groups = permission_manager.get_permission_groups()

        selected_permissions = []
        cols = st.columns(2)

        for i, (group_name, group_perms) in enumerate(permission_groups.items()):
            with cols[i % 2]:
                with st.expander(f"📁 {group_name}"):
                    for perm in group_perms:
                        if perm in permission_manager.available_permissions:
                            arabic_name = permission_manager.permission_translations.get(perm, perm)
                            is_selected = st.checkbox(
                                arabic_name,
                                value=perm in current_permissions,
                                key=f"perm_{emp_id}_{perm}"
                            )
                            if is_selected:
                                selected_permissions.append(perm)

        # حفظ التغييرات
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("💾 حفظ الصلاحيات", use_container_width=True):
                # التحقق من صحة التعيين
                is_valid, message = permission_manager.validate_permission_assignment(emp_id, selected_permissions)

                if is_valid:
                    if permission_manager.update_employee_permissions(emp_id, selected_permissions):
                        st.success("تم حفظ الصلاحيات بنجاح")

                        # تسجيل في audit trail
                        from core.audit_trail import log_user_action
                        log_user_action(
                            'EmployeePermissions',
                            emp_id,
                            'UPDATE',
                            old_values={'permissions': current_permissions},
                            new_values={'permissions': selected_permissions}
                        )

                        st.rerun()
                    else:
                        st.error("فشل في حفظ الصلاحيات")
                else:
                    st.error(message)

        with col2:
            if st.button("🔄 إعادة تعيين", use_container_width=True):
                default_perms = permission_manager.default_permissions['Employee']
                if permission_manager.update_employee_permissions(emp_id, default_perms):
                    st.success("تم إعادة تعيين الصلاحيات الافتراضية")

                    # تسجيل في audit trail
                    from core.audit_trail import log_user_action
                    log_user_action(
                        'EmployeePermissions',
                        emp_id,
                        'UPDATE',
                        old_values={'permissions': current_permissions},
                        new_values={'permissions': default_perms}
                    )

                    st.rerun()
                else:
                    st.error("فشل في إعادة التعيين")

    except Exception as e:
        st.error(f"خطأ في النظام: {str(e)}")
        permission_manager.logger.error(f"Error in permission manager UI: {str(e)}")

def display_permission_matrix():
    """عرض مصفوفة الصلاحيات في Streamlit"""
    st.subheader("📊 مصفوفة صلاحيات الموظفين")

    require_permission('ADMIN', "يجب أن تكون مديراً لعرض مصفوفة الصلاحيات")

    matrix = permission_manager.get_permission_matrix()

    if not matrix:
        st.info("لا توجد بيانات صلاحيات متاحة")
        return

    # تحويل إلى DataFrame للعرض
    import pandas as pd

    # إنشاء DataFrame
    df_data = []
    for emp_name, perms in matrix.items():
        row = {'الموظف': emp_name}
        row.update({permission_manager.permission_translations.get(perm, perm): '✅' if has_perm else '❌'
                   for perm, has_perm in perms.items()})
        df_data.append(row)

    df = pd.DataFrame(df_data)

    # عرض الجدول
    st.dataframe(df, use_container_width=True)

    # إحصائيات
    st.subheader("إحصائيات الصلاحيات")

    total_employees = len(matrix)
    permissions_stats = {}

    for perm in permission_manager.available_permissions.keys():
        arabic_name = permission_manager.permission_translations.get(perm, perm)
        count = sum(1 for emp_perms in matrix.values() if emp_perms.get(perm, False))
        permissions_stats[arabic_name] = count

    # عرض الإحصائيات
    col1, col2 = st.columns(2)

    with col1:
        st.metric("إجمالي الموظفين", total_employees)

    with col2:
        most_common_perm = max(permissions_stats.items(), key=lambda x: x[1])
        st.metric("الصلاحية الأكثر شيوعاً", f"{most_common_perm[0]} ({most_common_perm[1]})")

    # رسم بياني
    if permissions_stats:
        chart_data = pd.DataFrame(list(permissions_stats.items()), columns=['الصلاحية', 'عدد الموظفين'])
        st.bar_chart(chart_data.set_index('الصلاحية'))