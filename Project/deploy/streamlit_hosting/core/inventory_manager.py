"""
نظام إدارة المخزون المتكامل - Petrol Pump Management System
يوفر هذا النظام إدارة متقدمة للمخزون مع تحديث تلقائي لمستويات الوقود
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from database import get_connection
import streamlit as st

# إعداد نظام التسجيل
logging.basicConfig(
    filename='inventory_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class InventoryManager:
    """مدير المخزون المتقدم"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_fuel_sale(self, tank_id: str, fuel_amount: float) -> Tuple[bool, str]:
        """
        التحقق من إمكانية بيع كمية الوقود المطلوبة

        Args:
            tank_id: معرف الخزان
            fuel_amount: كمية الوقود المطلوبة

        Returns:
            Tuple[bool, str]: (صحيح/خطأ, رسالة)
        """
        try:
            conn = get_connection()
            if not conn:
                return False, "فشل في الاتصال بقاعدة البيانات"

            c = conn.cursor()

            # التحقق من وجود الخزان
            c.execute("SELECT Current_Amount, Capacity FROM FuelTank WHERE FuelTank_ID = %s", (tank_id,))
            tank_data = c.fetchone()

            if not tank_data:
                conn.close()
                return False, f"الخزان {tank_id} غير موجود"

            current_amount, capacity = tank_data

            # التحقق من توفر الكمية
            if current_amount < fuel_amount:
                conn.close()
                return False, f"كمية الوقود المتاحة ({current_amount} لتر) أقل من المطلوب ({fuel_amount} لتر)"

            # التحقق من عدم تجاوز الحد الأدنى (10% من السعة)
            min_level = capacity * 0.1
            if (current_amount - fuel_amount) < min_level:
                conn.close()
                return False, f"بعد البيع سيصل مستوى الوقود إلى أقل من الحد الأدنى المسموح ({min_level} لتر)"

            conn.close()
            return True, "الكمية متاحة للبيع"

        except Exception as e:
            self.logger.error(f"خطأ في التحقق من بيع الوقود: {str(e)}")
            return False, f"خطأ في النظام: {str(e)}"

    def update_inventory_on_sale(self, tank_id: str, fuel_amount: float, employee_id: str = None) -> Tuple[bool, str]:
        """
        تحديث المخزون عند البيع مع تسجيل العملية

        Args:
            tank_id: معرف الخزان
            fuel_amount: كمية الوقود المباعة
            employee_id: معرف الموظف (اختياري)

        Returns:
            Tuple[bool, str]: (نجح/فشل, رسالة)
        """
        conn = get_connection()
        if not conn:
            return False, "فشل في الاتصال بقاعدة البيانات"

        try:
            c = conn.cursor()

            # بدء المعاملة
            conn.begin()

            # التحقق من صحة البيع
            is_valid, message = self.validate_fuel_sale(tank_id, fuel_amount)
            if not is_valid:
                conn.rollback()
                conn.close()
                return False, message

            # تحديث مستوى الوقود في الخزان
            c.execute("""
                UPDATE FuelTank
                SET Current_Amount = Current_Amount - %s
                WHERE FuelTank_ID = %s
            """, (fuel_amount, tank_id))

            # تسجيل حركة المخزون
            c.execute("""
                INSERT INTO InventoryTransactions
                (Tank_ID, Transaction_Type, Amount, Employee_ID, Transaction_Date, Notes)
                VALUES (%s, 'SALE', %s, %s, %s, %s)
            """, (tank_id, fuel_amount, employee_id, datetime.now(),
                  f"بيع وقود - كمية: {fuel_amount} لتر"))

            # التحقق من مستوى الوقود المنخفض
            c.execute("SELECT Current_Amount, Capacity FROM FuelTank WHERE FuelTank_ID = %s", (tank_id,))
            current_amount, capacity = c.fetchone()

            low_level_threshold = capacity * 0.15  # 15% من السعة
            if current_amount <= low_level_threshold:
                # تسجيل تنبيه مستوى منخفض
                c.execute("""
                    INSERT INTO InventoryAlerts
                    (Tank_ID, Alert_Type, Message, Severity, Created_Date)
                    VALUES (%s, 'LOW_FUEL', %s, 'HIGH', %s)
                """, (tank_id, f"مستوى الوقود منخفض: {current_amount} لتر متبقي", datetime.now()))

            # تأكيد المعاملة
            conn.commit()
            conn.close()

            self.logger.info(f"تم تحديث المخزون بنجاح - خزان: {tank_id}, كمية: {fuel_amount}")
            return True, "تم تحديث المخزون بنجاح"

        except Exception as e:
            conn.rollback()
            conn.close()
            self.logger.error(f"خطأ في تحديث المخزون: {str(e)}")
            return False, f"فشل في تحديث المخزون: {str(e)}"

    def update_inventory_on_supply(self, tank_id: str, fuel_amount: float, supplier_name: str = None) -> Tuple[bool, str]:
        """
        تحديث المخزون عند التوريد

        Args:
            tank_id: معرف الخزان
            fuel_amount: كمية الوقود الموردة
            supplier_name: اسم المورد

        Returns:
            Tuple[bool, str]: (نجح/فشل, رسالة)
        """
        conn = get_connection()
        if not conn:
            return False, "فشل في الاتصال بقاعدة البيانات"

        try:
            c = conn.cursor()
            conn.begin()

            # التحقق من وجود الخزان
            c.execute("SELECT Current_Amount, Capacity FROM FuelTank WHERE FuelTank_ID = %s", (tank_id,))
            tank_data = c.fetchone()

            if not tank_data:
                conn.rollback()
                conn.close()
                return False, f"الخزان {tank_id} غير موجود"

            current_amount, capacity = tank_data

            # التحقق من عدم تجاوز السعة
            if (current_amount + fuel_amount) > capacity:
                conn.rollback()
                conn.close()
                return False, f"الكمية المضافة ستتجاوز سعة الخزان ({capacity} لتر)"

            # تحديث مستوى الوقود
            c.execute("""
                UPDATE FuelTank
                SET Current_Amount = Current_Amount + %s
                WHERE FuelTank_ID = %s
            """, (fuel_amount, tank_id))

            # تسجيل حركة المخزون
            c.execute("""
                INSERT INTO InventoryTransactions
                (Tank_ID, Transaction_Type, Amount, Transaction_Date, Notes)
                VALUES (%s, 'SUPPLY', %s, %s, %s)
            """, (tank_id, fuel_amount, datetime.now(),
                  f"توريد وقود من {supplier_name} - كمية: {fuel_amount} لتر"))

            # إزالة تنبيهات المستوى المنخفض إذا تم تجاوز الحد
            c.execute("""
                DELETE FROM InventoryAlerts
                WHERE Tank_ID = %s AND Alert_Type = 'LOW_FUEL'
            """, (tank_id,))

            conn.commit()
            conn.close()

            self.logger.info(f"تم تحديث المخزون عند التوريد - خزان: {tank_id}, كمية: {fuel_amount}")
            return True, "تم تحديث المخزون عند التوريد بنجاح"

        except Exception as e:
            conn.rollback()
            conn.close()
            self.logger.error(f"خطأ في تحديث المخزون عند التوريد: {str(e)}")
            return False, f"فشل في تحديث المخزون: {str(e)}"

    def get_inventory_status(self) -> List[Dict]:
        """
        الحصول على حالة المخزون لجميع الخزانات

        Returns:
            List[Dict]: قائمة بحالة كل خزان
        """
        try:
            conn = get_connection()
            if not conn:
                return []

            c = conn.cursor()

            c.execute("""
                SELECT
                    ft.FuelTank_ID,
                    ft.Fuel_Type,
                    ft.Capacity,
                    ft.Current_Amount,
                    ROUND((ft.Current_Amount / ft.Capacity) * 100, 2) as Fill_Percentage,
                    CASE
                        WHEN (ft.Current_Amount / ft.Capacity) <= 0.15 THEN 'منخفض جداً'
                        WHEN (ft.Current_Amount / ft.Capacity) <= 0.30 THEN 'منخفض'
                        WHEN (ft.Current_Amount / ft.Capacity) <= 0.80 THEN 'متوسط'
                        ELSE 'مرتفع'
                    END as Status
                FROM FuelTank ft
                ORDER BY ft.FuelTank_ID
            """)

            results = c.fetchall()
            conn.close()

            inventory_status = []
            for row in results:
                inventory_status.append({
                    'tank_id': row[0],
                    'fuel_type': row[1],
                    'capacity': row[2],
                    'current_amount': row[3],
                    'fill_percentage': row[4],
                    'status': row[5]
                })

            return inventory_status

        except Exception as e:
            self.logger.error(f"خطأ في الحصول على حالة المخزون: {str(e)}")
            return []

    def get_inventory_alerts(self) -> List[Dict]:
        """
        الحصول على تنبيهات المخزون

        Returns:
            List[Dict]: قائمة بالتنبيهات
        """
        try:
            conn = get_connection()
            if not conn:
                return []

            c = conn.cursor()

            c.execute("""
                SELECT
                    ia.Alert_ID,
                    ia.Tank_ID,
                    ft.Fuel_Type,
                    ia.Alert_Type,
                    ia.Message,
                    ia.Severity,
                    ia.Created_Date,
                    ia.Resolved
                FROM InventoryAlerts ia
                JOIN FuelTank ft ON ia.Tank_ID = ft.FuelTank_ID
                WHERE ia.Resolved = FALSE
                ORDER BY ia.Created_Date DESC
            """)

            results = c.fetchall()
            conn.close()

            alerts = []
            for row in results:
                alerts.append({
                    'alert_id': row[0],
                    'tank_id': row[1],
                    'fuel_type': row[2],
                    'alert_type': row[3],
                    'message': row[4],
                    'severity': row[5],
                    'created_date': row[6],
                    'resolved': row[7]
                })

            return alerts

        except Exception as e:
            self.logger.error(f"خطأ في الحصول على تنبيهات المخزون: {str(e)}")
            return []

    def resolve_alert(self, alert_id: int) -> bool:
        """
        حل تنبيه محدد

        Args:
            alert_id: معرف التنبيه

        Returns:
            bool: نجح/فشل
        """
        try:
            conn = get_connection()
            if not conn:
                return False

            c = conn.cursor()

            c.execute("""
                UPDATE InventoryAlerts
                SET Resolved = TRUE, Resolved_Date = %s
                WHERE Alert_ID = %s
            """, (datetime.now(), alert_id))

            conn.commit()
            conn.close()

            self.logger.info(f"تم حل التنبيه {alert_id}")
            return True

        except Exception as e:
            self.logger.error(f"خطأ في حل التنبيه: {str(e)}")
            return False

# إنشاء instance عالمي
inventory_manager = InventoryManager()

# دوال مساعدة للاستخدام في Streamlit
def validate_and_update_inventory_on_sale(tank_id: str, fuel_amount: float, employee_id: str = None):
    """دالة مساعدة للتحقق وتحديث المخزون عند البيع"""
    success, message = inventory_manager.update_inventory_on_sale(tank_id, fuel_amount, employee_id)
    if success:
        st.success(message)
    else:
        st.error(message)
    return success

def validate_and_update_inventory_on_supply(tank_id: str, fuel_amount: float, supplier_name: str = None):
    """دالة مساعدة للتحقق وتحديث المخزون عند التوريد"""
    success, message = inventory_manager.update_inventory_on_supply(tank_id, fuel_amount, supplier_name)
    if success:
        st.success(message)
    else:
        st.error(message)
    return success

def display_inventory_status():
    """عرض حالة المخزون في Streamlit"""
    st.subheader("📊 حالة المخزون")

    inventory_status = inventory_manager.get_inventory_status()

    if not inventory_status:
        st.warning("لا توجد بيانات مخزون متاحة")
        return

    # عرض ملخص
    total_capacity = sum(item['capacity'] for item in inventory_status)
    total_current = sum(item['current_amount'] for item in inventory_status)
    avg_fill = (total_current / total_capacity * 100) if total_capacity > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("إجمالي السعة", f"{total_capacity:,.0f} لتر")
    with col2:
        st.metric("الكمية الحالية", f"{total_current:,.0f} لتر")
    with col3:
        st.metric("متوسط التعبئة", f"{avg_fill:.1f}%")
    with col4:
        low_tanks = len([t for t in inventory_status if t['status'] in ['منخفض', 'منخفض جداً']])
        st.metric("خزانات منخفضة", low_tanks)

    # عرض تفصيلي
    st.subheader("تفاصيل الخزانات")
    for tank in inventory_status:
        with st.expander(f"🛢️ خزان {tank['tank_id']} - {tank['fuel_type']}"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(f"**السعة:** {tank['capacity']} لتر")
            with col2:
                st.write(f"**الكمية الحالية:** {tank['current_amount']} لتر")
            with col3:
                st.write(f"**نسبة التعبئة:** {tank['fill_percentage']}%")
            with col4:
                status_color = {
                    'مرتفع': '🟢',
                    'متوسط': '🟡',
                    'منخفض': '🟠',
                    'منخفض جداً': '🔴'
                }
                st.write(f"**الحالة:** {status_color.get(tank['status'], '⚪')} {tank['status']}")

            # شريط التقدم
            st.progress(min(tank['fill_percentage'] / 100, 1.0))

def display_inventory_alerts():
    """عرض تنبيهات المخزون في Streamlit"""
    st.subheader("🚨 تنبيهات المخزون")

    alerts = inventory_manager.get_inventory_alerts()

    if not alerts:
        st.success("لا توجد تنبيهات نشطة")
        return

    for alert in alerts:
        severity_color = {
            'LOW': '🟡',
            'MEDIUM': '🟠',
            'HIGH': '🔴',
            'CRITICAL': '🔴'
        }

        with st.expander(f"{severity_color.get(alert['severity'], '⚪')} {alert['alert_type']} - خزان {alert['tank_id']}"):
            st.write(f"**النوع:** {alert['fuel_type']}")
            st.write(f"**الرسالة:** {alert['message']}")
            st.write(f"**التاريخ:** {alert['created_date']}")

            if st.button(f"حل التنبيه", key=f"resolve_{alert['alert_id']}"):
                if inventory_manager.resolve_alert(alert['alert_id']):
                    st.success("تم حل التنبيه بنجاح")
                    st.rerun()
                else:
                    st.error("فشل في حل التنبيه")