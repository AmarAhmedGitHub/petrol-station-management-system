"""
ربط الموظفين بالمحطات مع فلترة البيانات - Petrol Pump Management System
يوفر هذا النظام ربط منطقي بين الموظفين والمحطات مع فلترة البيانات حسب الصلاحيات
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from database import get_connection
import streamlit as st

# إعداد نظام التسجيل
logging.basicConfig(
    filename='employee_station_linker.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class EmployeeStationLinker:
    """مدير ربط الموظفين بالمحطات"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_employee_stations(self, employee_id: str) -> List[Dict[str, Any]]:
        """
        الحصول على المحطات المرتبطة بموظف معين

        Args:
            employee_id: معرف الموظف

        Returns:
            List[Dict]: قائمة المحطات المرتبطة
        """
        try:
            conn = get_connection()
            if not conn:
                return []

            c = conn.cursor()

            # الحصول على المحطات من خلال PumpDirectory
            c.execute("""
                SELECT DISTINCT
                    pd.Petrolpump_No,
                    pp.Petrolpump_Name,
                    pp.Company_Name,
                    pp.City,
                    pp.State,
                    pd.FuelTank_ID,
                    ft.Fuel_Type,
                    ft.Current_Amount,
                    ft.Capacity
                FROM PumpDirectory pd
                JOIN Petrolpump pp ON pd.Petrolpump_No = pp.Registration_No
                LEFT JOIN FuelTank ft ON pd.FuelTank_ID = ft.FuelTank_ID
                WHERE pd.Employee_ID = %s
                ORDER BY pp.Petrolpump_Name
            """, (employee_id,))

            stations = []
            for row in c.fetchall():
                stations.append({
                    'station_id': row[0],
                    'station_name': row[1],
                    'company_name': row[2],
                    'city': row[3],
                    'state': row[4],
                    'tank_id': row[5],
                    'fuel_type': row[6],
                    'current_amount': row[7],
                    'capacity': row[8]
                })

            # إذا لم يكن هناك ربط محدد، إرجاع المحطة من Employee
            if not stations:
                c.execute("""
                    SELECT
                        e.Petrolpump_No,
                        pp.Petrolpump_Name,
                        pp.Company_Name,
                        pp.City,
                        pp.State
                    FROM Employee e
                    JOIN Petrolpump pp ON e.Petrolpump_No = pp.Registration_No
                    WHERE e.Employee_ID = %s
                """, (employee_id,))

                emp_station = c.fetchone()
                if emp_station:
                    stations.append({
                        'station_id': emp_station[0],
                        'station_name': emp_station[1],
                        'company_name': emp_station[2],
                        'city': emp_station[3],
                        'state': emp_station[4],
                        'tank_id': None,
                        'fuel_type': None,
                        'current_amount': None,
                        'capacity': None
                    })

            conn.close()
            return stations

        except Exception as e:
            self.logger.error(f"Error getting employee stations: {str(e)}")
            return []

    def assign_employee_to_station(self, employee_id: str, station_id: str,
                                 tank_id: Optional[str] = None) -> Tuple[bool, str]:
        """
        ربط موظف بمحطة وخزان محدد

        Args:
            employee_id: معرف الموظف
            station_id: معرف المحطة
            tank_id: معرف الخزان (اختياري)

        Returns:
            Tuple[bool, str]: (نجح/فشل, رسالة)
        """
        try:
            conn = get_connection()
            if not conn:
                return False, "فشل في الاتصال بقاعدة البيانات"

            c = conn.cursor()
            conn.begin()

            # التحقق من وجود الموظف
            c.execute("SELECT COUNT(*) FROM Employee WHERE Employee_ID = %s", (employee_id,))
            if c.fetchone()[0] == 0:
                conn.rollback()
                conn.close()
                return False, f"الموظف {employee_id} غير موجود"

            # التحقق من وجود المحطة
            c.execute("SELECT COUNT(*) FROM Petrolpump WHERE Registration_No = %s", (station_id,))
            if c.fetchone()[0] == 0:
                conn.rollback()
                conn.close()
                return False, f"المحطة {station_id} غير موجودة"

            # التحقق من وجود الخزان إذا تم تحديده
            if tank_id:
                c.execute("SELECT COUNT(*) FROM FuelTank WHERE FuelTank_ID = %s", (tank_id,))
                if c.fetchone()[0] == 0:
                    conn.rollback()
                    conn.close()
                    return False, f"الخزان {tank_id} غير موجود"

                # التحقق من أن الخزان ينتمي للمحطة
                c.execute("""
                    SELECT COUNT(*) FROM Petrolpump p
                    JOIN FuelTank ft ON p.FuelTank_ID = ft.FuelTank_ID
                    WHERE p.Registration_No = %s AND ft.FuelTank_ID = %s
                """, (station_id, tank_id))
                if c.fetchone()[0] == 0:
                    conn.rollback()
                    conn.close()
                    return False, f"الخزان {tank_id} لا ينتمي للمحطة {station_id}"

            # حذف الربط القديم
            c.execute("DELETE FROM PumpDirectory WHERE Employee_ID = %s", (employee_id,))

            # إضافة الربط الجديد
            c.execute("""
                INSERT INTO PumpDirectory (Petrolpump_No, FuelTank_ID, Employee_ID)
                VALUES (%s, %s, %s)
            """, (station_id, tank_id, employee_id))

            # تحديث Employee.Petrolpump_No
            c.execute("UPDATE Employee SET Petrolpump_No = %s WHERE Employee_ID = %s",
                     (station_id, employee_id))

            conn.commit()
            conn.close()

            self.logger.info(f"Assigned employee {employee_id} to station {station_id}, tank {tank_id}")
            return True, "تم ربط الموظف بالمحطة بنجاح"

        except Exception as e:
            conn.rollback()
            conn.close()
            self.logger.error(f"Error assigning employee to station: {str(e)}")
            return False, f"فشل في ربط الموظف بالمحطة: {str(e)}"

    def get_station_employees(self, station_id: str) -> List[Dict[str, Any]]:
        """
        الحصول على موظفي محطة معينة

        Args:
            station_id: معرف المحطة

        Returns:
            List[Dict]: قائمة الموظفين
        """
        try:
            conn = get_connection()
            if not conn:
                return []

            c = conn.cursor()

            c.execute("""
                SELECT DISTINCT
                    e.Employee_ID,
                    e.Emp_Name,
                    e.Designation,
                    pd.FuelTank_ID,
                    ft.Fuel_Type,
                    GROUP_CONCAT(ep.Permission SEPARATOR ', ') as permissions
                FROM Employee e
                LEFT JOIN PumpDirectory pd ON e.Employee_ID = pd.Employee_ID
                LEFT JOIN FuelTank ft ON pd.FuelTank_ID = ft.FuelTank_ID
                LEFT JOIN EmployeePermissions ep ON e.Employee_ID = ep.Employee_ID
                WHERE e.Petrolpump_No = %s OR pd.Petrolpump_No = %s
                GROUP BY e.Employee_ID, e.Emp_Name, e.Designation, pd.FuelTank_ID, ft.Fuel_Type
                ORDER BY e.Emp_Name
            """, (station_id, station_id))

            employees = []
            for row in c.fetchall():
                employees.append({
                    'employee_id': row[0],
                    'employee_name': row[1],
                    'designation': row[2],
                    'tank_id': row[3],
                    'fuel_type': row[4],
                    'permissions': row[5] if row[5] else 'لا توجد صلاحيات محددة'
                })

            conn.close()
            return employees

        except Exception as e:
            self.logger.error(f"Error getting station employees: {str(e)}")
            return []

    def filter_data_by_employee_station(self, employee_id: str, table_name: str,
                                      additional_filters: Optional[Dict[str, Any]] = None) -> str:
        """
        إنشاء فلتر SQL للبيانات حسب محطة الموظف

        Args:
            employee_id: معرف الموظف
            table_name: اسم الجدول
            additional_filters: فلاتر إضافية

        Returns:
            str: شرط WHERE للـ SQL
        """
        try:
            stations = self.get_employee_stations(employee_id)
            if not stations:
                return "1=0"  # لا توجد محطات = لا توجد بيانات

            station_ids = [s['station_id'] for s in stations]

            # تحديد عمود المحطة حسب الجدول
            station_columns = {
                'Invoice': 'Petrolpump_No',
                'Tanker': 'Petrolpump_No',
                'FuelSupply': 'FuelTank_ID',  # غير مباشر
                'FuelTank': 'FuelTank_ID',
                'Petrolpump': 'Registration_No',
                'Employee': 'Petrolpump_No'
            }

            station_column = station_columns.get(table_name)
            if not station_column:
                return "1=1"  # لا فلترة

            # إنشاء شرط IN
            placeholders = ','.join(['%s'] * len(station_ids))
            condition = f"{station_column} IN ({placeholders})"

            # إضافة فلاتر إضافية
            if additional_filters:
                for key, value in additional_filters.items():
                    if isinstance(value, list):
                        placeholders = ','.join(['%s'] * len(value))
                        condition += f" AND {key} IN ({placeholders})"
                    else:
                        condition += f" AND {key} = %s"

            return condition

        except Exception as e:
            self.logger.error(f"Error creating station filter: {str(e)}")
            return "1=1"  # لا فلترة في حالة الخطأ

    def get_employee_dashboard_data(self, employee_id: str) -> Dict[str, Any]:
        """
        الحصول على بيانات لوحة تحكم الموظف المفلترة حسب محطته

        Args:
            employee_id: معرف الموظف

        Returns:
            Dict: بيانات لوحة التحكم
        """
        try:
            stations = self.get_employee_stations(employee_id)
            if not stations:
                return {'error': 'لا توجد محطات مرتبطة بالموظف'}

            station_ids = [s['station_id'] for s in stations]

            conn = get_connection()
            if not conn:
                return {'error': 'فشل في الاتصال بقاعدة البيانات'}

            c = conn.cursor()

            # إحصائيات المبيعات للمحطات المرتبطة
            placeholders = ','.join(['%s'] * len(station_ids))
            c.execute(f"""
                SELECT
                    COUNT(*) as total_invoices,
                    COALESCE(SUM(Total_Price), 0) as total_sales,
                    COALESCE(SUM(Fuel_Amount), 0) as total_fuel
                FROM Invoice
                WHERE Petrolpump_No IN ({placeholders})
            """, station_ids)

            sales_stats = c.fetchone()

            # إحصائيات الخزانات
            tank_stats = []
            for station in stations:
                if station['tank_id']:
                    c.execute("""
                        SELECT Fuel_Type, Current_Amount, Capacity,
                               ROUND((Current_Amount / Capacity) * 100, 2) as fill_percentage
                        FROM FuelTank
                        WHERE FuelTank_ID = %s
                    """, (station['tank_id'],))

                    tank_data = c.fetchone()
                    if tank_data:
                        tank_stats.append({
                            'station_name': station['station_name'],
                            'fuel_type': tank_data[0],
                            'current_amount': tank_data[1],
                            'capacity': tank_data[2],
                            'fill_percentage': tank_data[3]
                        })

            # فواتير اليوم
            from datetime import date
            today = date.today()
            c.execute(f"""
                SELECT COUNT(*) as today_invoices,
                       COALESCE(SUM(Total_Price), 0) as today_sales
                FROM Invoice
                WHERE DATE(Date) = %s AND Petrolpump_No IN ({placeholders})
            """, [today] + station_ids)

            today_stats = c.fetchone()

            conn.close()

            return {
                'stations': stations,
                'sales_stats': {
                    'total_invoices': sales_stats[0],
                    'total_sales': sales_stats[1],
                    'total_fuel': sales_stats[2]
                },
                'tank_stats': tank_stats,
                'today_stats': {
                    'today_invoices': today_stats[0],
                    'today_sales': today_stats[1]
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting employee dashboard data: {str(e)}")
            return {'error': str(e)}

    def validate_station_access(self, employee_id: str, station_id: str) -> bool:
        """
        التحقق من إمكانية وصول الموظف لمحطة معينة

        Args:
            employee_id: معرف الموظف
            station_id: معرف المحطة

        Returns:
            bool: True إذا كان الموظف يمكنه الوصول
        """
        try:
            stations = self.get_employee_stations(employee_id)
            station_ids = [s['station_id'] for s in stations]
            return station_id in station_ids

        except Exception as e:
            self.logger.error(f"Error validating station access: {str(e)}")
            return False

# إنشاء instance عالمي
employee_station_linker = EmployeeStationLinker()

# دوال مساعدة للاستخدام في Streamlit
def display_employee_stations(employee_id: str):
    """عرض المحطات المرتبطة بالموظف في Streamlit"""
    st.subheader("🏭 محطاتي")

    stations = employee_station_linker.get_employee_stations(employee_id)

    if not stations:
        st.info("لا توجد محطات مرتبطة بك")
        return

    for station in stations:
        with st.expander(f"⛽ {station['station_name']} - {station['city']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**رقم المحطة:** {station['station_id']}")
                st.write(f"**الشركة:** {station['company_name'] or 'غير محدد'}")
                st.write(f"**المدينة:** {station['city']}")

            with col2:
                if station['tank_id']:
                    st.write(f"**خزان الوقود:** {station['tank_id']}")
                    st.write(f"**نوع الوقود:** {station['fuel_type'] or 'غير محدد'}")
                    st.write(f"**الكمية الحالية:** {station['current_amount'] or 0} لتر")
                    st.write(f"**السعة:** {station['capacity'] or 0} لتر")

                    # شريط التقدم
                    if station['capacity'] and station['capacity'] > 0:
                        progress = min((station['current_amount'] or 0) / station['capacity'], 1.0)
                        st.progress(progress)
                        st.write(f"**نسبة التعبئة:** {progress * 100:.1f}%")
                else:
                    st.write("**خزان الوقود:** غير مرتبط")

def assign_employee_to_station_ui():
    """واجهة ربط الموظفين بالمحطات في Streamlit"""
    st.subheader("🔗 ربط الموظفين بالمحطات")

    # التحقق من الصلاحية
    from core.permission_manager import check_permission
    if not check_permission('ADMIN') and not check_permission('MANAGEMENT'):
        st.error("ليس لديك صلاحية للوصول لهذه الصفحة")
        return

    try:
        conn = get_connection()
        if not conn:
            st.error("فشل في الاتصال بقاعدة البيانات")
            return

        c = conn.cursor()

        # اختيار الموظف
        c.execute("SELECT Employee_ID, Emp_Name FROM Employee ORDER BY Emp_Name")
        employees = c.fetchall()
        conn.close()

        if not employees:
            st.info("لا يوجد موظفون مسجلون")
            return

        emp_options = {f"{name} ({emp_id})": emp_id for emp_id, name in employees}
        selected_emp = st.selectbox("اختر الموظف:", list(emp_options.keys()), key="assign_emp")

        # اختيار المحطة
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT Registration_No, Petrolpump_Name, City FROM Petrolpump ORDER BY Petrolpump_Name")
        stations = c.fetchall()
        conn.close()

        if not stations:
            st.info("لا توجد محطات مسجلة")
            return

        station_options = {f"{name} - {city} ({reg_no})": reg_no for reg_no, name, city in stations}
        selected_station = st.selectbox("اختر المحطة:", list(station_options.keys()), key="assign_station")

        # اختيار الخزان (اختياري)
        conn = get_connection()
        c = conn.cursor()
        station_id = station_options[selected_station]
        c.execute("""
            SELECT ft.FuelTank_ID, ft.Fuel_Type, ft.Current_Amount, ft.Capacity
            FROM FuelTank ft
            JOIN Petrolpump p ON ft.FuelTank_ID = p.FuelTank_ID
            WHERE p.Registration_No = %s
        """, (station_id,))
        tanks = c.fetchall()
        conn.close()

        tank_options = {f"خزان {tank_id} - {fuel_type} ({current}/{capacity} لتر)": tank_id
                       for tank_id, fuel_type, current, capacity in tanks}
        tank_options["عدم تحديد خزان محدد"] = None

        selected_tank = st.selectbox("اختر خزان الوقود (اختياري):", list(tank_options.keys()), key="assign_tank")

        # زر الربط
        if st.button("🔗 ربط الموظف بالمحطة", use_container_width=True):
            emp_id = emp_options[selected_emp]
            tank_id = tank_options[selected_tank]

            success, message = employee_station_linker.assign_employee_to_station(
                emp_id, station_id, tank_id
            )

            if success:
                st.success(message)

                # تسجيل في audit trail
                from core.audit_trail import log_user_action
                log_user_action(
                    'PumpDirectory',
                    f"{emp_id}_{station_id}",
                    'INSERT',
                    new_values={
                        'employee_id': emp_id,
                        'station_id': station_id,
                        'tank_id': tank_id
                    }
                )

                st.rerun()
            else:
                st.error(message)

    except Exception as e:
        st.error(f"خطأ في النظام: {str(e)}")
        employee_station_linker.logger.error(f"Error in assign employee UI: {str(e)}")

def display_station_employees(station_id: Optional[str] = None):
    """عرض موظفي المحطة في Streamlit"""
    st.subheader("👥 موظفو المحطة")

    if not station_id:
        # اختيار المحطة
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT Registration_No, Petrolpump_Name, City FROM Petrolpump ORDER BY Petrolpump_Name")
            stations = c.fetchall()
            conn.close()

            if not stations:
                st.info("لا توجد محطات مسجلة")
                return

            station_options = {f"{name} - {city} ({reg_no})": reg_no for reg_no, name, city in stations}
            selected_station = st.selectbox("اختر المحطة:", list(station_options.keys()), key="station_emp_select")
            station_id = station_options[selected_station]

        except Exception as e:
            st.error(f"خطأ في تحميل المحطات: {str(e)}")
            return

    employees = employee_station_linker.get_station_employees(station_id)

    if not employees:
        st.info("لا يوجد موظفون مرتبطون بهذه المحطة")
        return

    for emp in employees:
        with st.expander(f"👤 {emp['employee_name']} ({emp['employee_id']})"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**المسمى الوظيفي:** {emp['designation'] or 'غير محدد'}")
                st.write(f"**الصلاحيات:** {emp['permissions']}")

            with col2:
                if emp['tank_id']:
                    st.write(f"**خزان الوقود:** {emp['tank_id']}")
                    st.write(f"**نوع الوقود:** {emp['fuel_type'] or 'غير محدد'}")
                else:
                    st.write("**خزان الوقود:** غير مرتبط")

def get_employee_filtered_data(employee_id: str, table_name: str, additional_filters: Optional[Dict[str, Any]] = None):
    """
    الحصول على بيانات مفلترة حسب محطة الموظف

    Args:
        employee_id: معرف الموظف
        table_name: اسم الجدول
        additional_filters: فلاتر إضافية

    Returns:
        str: شرط WHERE للـ SQL
    """
    return employee_station_linker.filter_data_by_employee_station(employee_id, table_name, additional_filters)