"""
ربط منطقي بين الخزانات والمضخات وسلسلة التوريد - Petrol Pump Management System
يوفر هذا النظام ربط متكامل بين جميع مكونات سلسلة التوريد
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from database import get_connection
import streamlit as st

# إعداد نظام التسجيل
logging.basicConfig(
    filename='supply_chain_integrator.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class SupplyChainIntegrator:
    """مدير ربط سلسلة التوريد"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_supply_chain_status(self) -> Dict[str, Any]:
        """
        الحصول على حالة سلسلة التوريد الكاملة

        Returns:
            Dict: حالة سلسلة التوريد
        """
        try:
            conn = get_connection()
            if not conn:
                return {}

            c = conn.cursor()

            # إحصائيات المحطات والخزانات
            c.execute("""
                SELECT
                    COUNT(DISTINCT p.Registration_No) as total_stations,
                    COUNT(DISTINCT ft.FuelTank_ID) as total_tanks,
                    SUM(ft.Capacity) as total_capacity,
                    SUM(ft.Current_Amount) as total_current_amount
                FROM Petrolpump p
                LEFT JOIN FuelTank ft ON p.FuelTank_ID = ft.FuelTank_ID
            """)

            station_stats = c.fetchone()

            # إحصائيات التوريد
            thirty_days_ago = datetime.now() - timedelta(days=30)
            c.execute("""
                SELECT
                    COUNT(*) as total_supplies,
                    SUM(Quantity) as total_supplied_quantity,
                    SUM(Total_Amount) as total_supply_cost,
                    COUNT(DISTINCT Supplier_Name) as unique_suppliers
                FROM FuelSupply
                WHERE Supply_Date >= %s
            """, (thirty_days_ago,))

            supply_stats = c.fetchone()

            # إحصائيات المبيعات
            c.execute("""
                SELECT
                    COUNT(*) as total_sales,
                    SUM(Fuel_Amount) as total_sold_quantity,
                    SUM(Total_Price) as total_sales_revenue
                FROM Invoice
                WHERE Date >= %s
            """, (thirty_days_ago,))

            sales_stats = c.fetchone()

            # إحصائيات الخزانات حسب المستوى
            c.execute("""
                SELECT
                    COUNT(CASE WHEN (Current_Amount / Capacity) <= 0.15 THEN 1 END) as critical_low,
                    COUNT(CASE WHEN (Current_Amount / Capacity) <= 0.30 AND (Current_Amount / Capacity) > 0.15 THEN 1 END) as low,
                    COUNT(CASE WHEN (Current_Amount / Capacity) > 0.30 THEN 1 END) as normal
                FROM FuelTank
                WHERE Capacity > 0
            """)

            tank_levels = c.fetchone()

            # ربط الموظفين بالمضخات
            c.execute("""
                SELECT
                    COUNT(DISTINCT pd.ID) as total_assignments,
                    COUNT(DISTINCT pd.Employee_ID) as assigned_employees,
                    COUNT(DISTINCT pd.Petrolpump_No) as stations_with_employees
                FROM PumpDirectory pd
            """)

            assignment_stats = c.fetchone()

            conn.close()

            return {
                'stations': {
                    'total_stations': station_stats[0],
                    'total_tanks': station_stats[1],
                    'total_capacity': station_stats[2] or 0,
                    'total_current_amount': station_stats[3] or 0
                },
                'supply': {
                    'total_supplies_30d': supply_stats[0],
                    'total_supplied_quantity_30d': supply_stats[1] or 0,
                    'total_supply_cost_30d': supply_stats[2] or 0,
                    'unique_suppliers': supply_stats[3]
                },
                'sales': {
                    'total_sales_30d': sales_stats[0],
                    'total_sold_quantity_30d': sales_stats[1] or 0,
                    'total_sales_revenue_30d': sales_stats[2] or 0
                },
                'tank_levels': {
                    'critical_low': tank_levels[0],
                    'low': tank_levels[1],
                    'normal': tank_levels[2]
                },
                'assignments': {
                    'total_assignments': assignment_stats[0],
                    'assigned_employees': assignment_stats[1],
                    'stations_with_employees': assignment_stats[2]
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting supply chain status: {str(e)}")
            return {}

    def get_station_supply_chain(self, station_id: str) -> Dict[str, Any]:
        """
        الحصول على سلسلة التوريد لمحطة معينة

        Args:
            station_id: معرف المحطة

        Returns:
            Dict: سلسلة التوريد للمحطة
        """
        try:
            conn = get_connection()
            if not conn:
                return {}

            c = conn.cursor()

            # معلومات المحطة والخزانات
            c.execute("""
                SELECT
                    p.Registration_No,
                    p.Petrolpump_Name,
                    p.Company_Name,
                    p.City,
                    ft.FuelTank_ID,
                    ft.Fuel_Type,
                    ft.Capacity,
                    ft.Current_Amount,
                    ROUND((ft.Current_Amount / ft.Capacity) * 100, 2) as fill_percentage
                FROM Petrolpump p
                LEFT JOIN FuelTank ft ON p.FuelTank_ID = ft.FuelTank_ID
                WHERE p.Registration_No = %s
            """, (station_id,))

            station_data = c.fetchone()
            if not station_data:
                conn.close()
                return {'error': 'المحطة غير موجودة'}

            # الموظفون المرتبطون
            c.execute("""
                SELECT
                    e.Employee_ID,
                    e.Emp_Name,
                    e.Designation,
                    pd.FuelTank_ID
                FROM PumpDirectory pd
                JOIN Employee e ON pd.Employee_ID = e.Employee_ID
                WHERE pd.Petrolpump_No = %s
            """, (station_id,))

            employees = c.fetchall()

            # آخر عمليات التوريد
            c.execute("""
                SELECT
                    fs.Supply_ID,
                    fs.Supply_Invoice_No,
                    fs.Supply_Date,
                    fs.Supplier_Name,
                    fs.Fuel_Type,
                    fs.Quantity,
                    fs.Unit_Price,
                    fs.Total_Amount
                FROM FuelSupply fs
                WHERE fs.FuelTank_ID = %s
                ORDER BY fs.Supply_Date DESC
                LIMIT 5
            """, (station_data[4],))

            recent_supplies = c.fetchall()

            # آخر المبيعات
            c.execute("""
                SELECT
                    i.Invoice_No,
                    i.Date,
                    i.Fuel_Amount,
                    i.Total_Price,
                    i.Customer_Code,
                    c.C_Name
                FROM Invoice i
                JOIN Customer c ON i.Customer_Code = c.Customer_Code
                WHERE i.Petrolpump_No = %s
                ORDER BY i.Date DESC
                LIMIT 10
            """, (station_id,))

            recent_sales = c.fetchall()

            # حركة المخزون
            c.execute("""
                SELECT
                    it.Transaction_ID,
                    it.Transaction_Type,
                    it.Amount,
                    it.Transaction_Date,
                    it.Notes,
                    e.Emp_Name
                FROM InventoryTransactions it
                LEFT JOIN Employee e ON it.Employee_ID = e.Employee_ID
                WHERE it.Tank_ID = %s
                ORDER BY it.Transaction_Date DESC
                LIMIT 10
            """, (station_data[4],))

            inventory_movements = c.fetchall()

            conn.close()

            return {
                'station_info': {
                    'id': station_data[0],
                    'name': station_data[1],
                    'company': station_data[2],
                    'city': station_data[3]
                },
                'tank_info': {
                    'id': station_data[4],
                    'fuel_type': station_data[5],
                    'capacity': station_data[6],
                    'current_amount': station_data[7],
                    'fill_percentage': station_data[8]
                } if station_data[4] else None,
                'employees': [{
                    'id': emp[0],
                    'name': emp[1],
                    'designation': emp[2],
                    'tank_id': emp[3]
                } for emp in employees],
                'recent_supplies': [{
                    'supply_id': supply[0],
                    'invoice_no': supply[1],
                    'date': supply[2],
                    'supplier': supply[3],
                    'fuel_type': supply[4],
                    'quantity': supply[5],
                    'unit_price': supply[6],
                    'total_amount': supply[7]
                } for supply in recent_supplies],
                'recent_sales': [{
                    'invoice_no': sale[0],
                    'date': sale[1],
                    'fuel_amount': sale[2],
                    'total_price': sale[3],
                    'customer_code': sale[4],
                    'customer_name': sale[5]
                } for sale in recent_sales],
                'inventory_movements': [{
                    'transaction_id': move[0],
                    'type': move[1],
                    'amount': move[2],
                    'date': move[3],
                    'notes': move[4],
                    'employee': move[5]
                } for move in inventory_movements]
            }

        except Exception as e:
            self.logger.error(f"Error getting station supply chain: {str(e)}")
            return {'error': str(e)}

    def optimize_supply_chain(self) -> Dict[str, Any]:
        """
        تحليل وتحسين سلسلة التوريد

        Returns:
            Dict: توصيات التحسين
        """
        try:
            status = self.get_supply_chain_status()

            recommendations = []

            # تحليل مستويات الخزانات
            tank_levels = status.get('tank_levels', {})
            if tank_levels.get('critical_low', 0) > 0:
                recommendations.append({
                    'type': 'critical',
                    'message': f"يوجد {tank_levels['critical_low']} خزان على مستوى حرج - يتطلب توريد فوري",
                    'action': 'schedule_emergency_supply'
                })

            if tank_levels.get('low', 0) > 0:
                recommendations.append({
                    'type': 'warning',
                    'message': f"يوجد {tank_levels['low']} خزان على مستوى منخفض - يُنصح بالتوريد",
                    'action': 'schedule_supply'
                })

            # تحليل التعيينات
            assignments = status.get('assignments', {})
            stations = status.get('stations', {})
            if assignments.get('stations_with_employees', 0) < stations.get('total_stations', 0):
                unassigned_stations = stations['total_stations'] - assignments['stations_with_employees']
                recommendations.append({
                    'type': 'info',
                    'message': f"يوجد {unassigned_stations} محطة بدون موظفين مخصصين",
                    'action': 'assign_employees'
                })

            # تحليل كفاءة المبيعات
            sales = status.get('sales', {})
            supply = status.get('supply', {})
            sold_quantity = sales.get('total_sold_quantity_30d', 0)
            supplied_quantity = supply.get('total_supplied_quantity_30d', 0)

            if supplied_quantity > 0:
                turnover_ratio = sold_quantity / supplied_quantity
                if turnover_ratio < 0.7:
                    recommendations.append({
                        'type': 'info',
                        'message': f"معدل دوران المخزون منخفض ({turnover_ratio:.2f}) - قد يشير إلى بطء المبيعات",
                        'action': 'review_sales_strategy'
                    })
                elif turnover_ratio > 1.5:
                    recommendations.append({
                        'type': 'warning',
                        'message': f"معدل دوران المخزون مرتفع ({turnover_ratio:.2f}) - قد يشير إلى نقص في المخزون",
                        'action': 'increase_supply_frequency'
                    })

            return {
                'recommendations': recommendations,
                'status_summary': status
            }

        except Exception as e:
            self.logger.error(f"Error optimizing supply chain: {str(e)}")
            return {'error': str(e)}

    def predict_supply_needs(self, station_id: str, days_ahead: int = 7) -> Dict[str, Any]:
        """
        توقع احتياجات التوريد للمحطة

        Args:
            station_id: معرف المحطة
            days_ahead: عدد الأيام المستقبلية

        Returns:
            Dict: توقعات الاحتياجات
        """
        try:
            conn = get_connection()
            if not conn:
                return {}

            c = conn.cursor()

            # الحصول على متوسط المبيعات اليومية لآخر 30 يوم
            c.execute("""
                SELECT
                    AVG(daily_sales) as avg_daily_sales,
                    STD(daily_sales) as std_daily_sales
                FROM (
                    SELECT DATE(Date) as sale_date, SUM(Fuel_Amount) as daily_sales
                    FROM Invoice
                    WHERE Petrolpump_No = %s AND Date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    GROUP BY DATE(Date)
                ) daily
            """, (station_id,))

            sales_pattern = c.fetchone()

            # معلومات الخزان الحالية
            c.execute("""
                SELECT ft.Current_Amount, ft.Capacity
                FROM Petrolpump p
                JOIN FuelTank ft ON p.FuelTank_ID = ft.FuelTank_ID
                WHERE p.Registration_No = %s
            """, (station_id,))

            tank_info = c.fetchone()

            conn.close()

            if not sales_pattern or not tank_info:
                return {'error': 'بيانات غير كافية للتوقع'}

            avg_daily_sales = sales_pattern[0] or 0
            std_daily_sales = sales_pattern[1] or 0
            current_amount = tank_info[0] or 0
            capacity = tank_info[1] or 0

            # حساب الاحتياجات المستقبلية
            predicted_sales = avg_daily_sales * days_ahead
            safety_stock = std_daily_sales * 2  # مخزون أمان = انحراف معياري × 2

            required_amount = predicted_sales + safety_stock
            available_amount = current_amount

            supply_needed = max(0, required_amount - available_amount)
            days_until_empty = available_amount / avg_daily_sales if avg_daily_sales > 0 else 999

            return {
                'station_id': station_id,
                'current_amount': current_amount,
                'capacity': capacity,
                'avg_daily_sales': avg_daily_sales,
                'predicted_sales': predicted_sales,
                'safety_stock': safety_stock,
                'required_amount': required_amount,
                'supply_needed': supply_needed,
                'days_until_empty': days_until_empty,
                'recommendation': 'supply_needed' if supply_needed > 0 else 'sufficient_stock',
                'urgency': 'high' if days_until_empty < 3 else 'medium' if days_until_empty < 7 else 'low'
            }

        except Exception as e:
            self.logger.error(f"Error predicting supply needs: {str(e)}")
            return {'error': str(e)}

# إنشاء instance عالمي
supply_chain_integrator = SupplyChainIntegrator()

# دوال مساعدة للاستخدام في Streamlit
def display_supply_chain_status():
    """عرض حالة سلسلة التوريد في Streamlit"""
    st.subheader("🔗 حالة سلسلة التوريد")

    status = supply_chain_integrator.get_supply_chain_status()

    if not status:
        st.error("فشل في تحميل حالة سلسلة التوريد")
        return

    # المقاييس الرئيسية
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        stations = status.get('stations', {})
        st.metric("إجمالي المحطات", stations.get('total_stations', 0))

    with col2:
        st.metric("إجمالي الخزانات", stations.get('total_tanks', 0))

    with col3:
        capacity = stations.get('total_capacity', 0)
        current = stations.get('total_current_amount', 0)
        st.metric("السعة الكلية", f"{capacity:,.0f} لتر")

    with col4:
        fill_rate = (current / capacity * 100) if capacity > 0 else 0
        st.metric("معدل التعبئة", f"{fill_rate:.1f}%")

    # مستويات الخزانات
    st.subheader("مستويات الخزانات")
    tank_levels = status.get('tank_levels', {})

    col1, col2, col3 = st.columns(3)

    with col1:
        critical = tank_levels.get('critical_low', 0)
        st.metric("خزانات حرجة", critical, delta=f"🔴 {critical}" if critical > 0 else "✅")

    with col2:
        low = tank_levels.get('low', 0)
        st.metric("خزانات منخفضة", low, delta=f"🟠 {low}" if low > 0 else "✅")

    with col3:
        normal = tank_levels.get('normal', 0)
        st.metric("خزانات طبيعية", normal, delta=f"🟢 {normal}")

    # إحصائيات التوريد والمبيعات
    st.subheader("النشاط التجاري (آخر 30 يوم)")
    supply = status.get('supply', {})
    sales = status.get('sales', {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("عمليات التوريد", supply.get('total_supplies_30d', 0))

    with col2:
        supplied_qty = supply.get('total_supplied_quantity_30d', 0)
        st.metric("الكمية الموردة", f"{supplied_qty:,.0f} لتر")

    with col3:
        st.metric("عمليات البيع", sales.get('total_sales_30d', 0))

    with col4:
        sold_qty = sales.get('total_sold_quantity_30d', 0)
        st.metric("الكمية المباعة", f"{sold_qty:,.0f} لتر")

def display_station_supply_chain(station_id: Optional[str] = None):
    """عرض سلسلة التوريد للمحطة في Streamlit"""
    st.subheader("⛽ سلسلة التوريد للمحطة")

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
            selected_station = st.selectbox("اختر المحطة:", list(station_options.keys()), key="station_sc_select")
            station_id = station_options[selected_station]

        except Exception as e:
            st.error(f"خطأ في تحميل المحطات: {str(e)}")
            return

    chain_data = supply_chain_integrator.get_station_supply_chain(station_id)

    if 'error' in chain_data:
        st.error(chain_data['error'])
        return

    # معلومات المحطة والخزان
    station_info = chain_data.get('station_info', {})
    tank_info = chain_data.get('tank_info')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("معلومات المحطة")
        st.write(f"**الاسم:** {station_info.get('name')}")
        st.write(f"**الشركة:** {station_info.get('company') or 'غير محدد'}")
        st.write(f"**المدينة:** {station_info.get('city')}")

    with col2:
        if tank_info:
            st.subheader("معلومات الخزان")
            st.write(f"**نوع الوقود:** {tank_info.get('fuel_type')}")
            st.write(f"**السعة:** {tank_info.get('capacity')} لتر")
            st.write(f"**الكمية الحالية:** {tank_info.get('current_amount')} لتر")
            st.write(f"**نسبة التعبئة:** {tank_info.get('fill_percentage')}%")

            # شريط التقدم
            progress = min(tank_info.get('fill_percentage', 0) / 100, 1.0)
            st.progress(progress)
        else:
            st.subheader("معلومات الخزان")
            st.info("لا يوجد خزان مرتبط بالمحطة")

    # الموظفون المرتبطون
    employees = chain_data.get('employees', [])
    if employees:
        st.subheader("الموظفون المرتبطون")
        for emp in employees:
            st.write(f"• {emp['name']} ({emp['designation']}) - خزان: {emp['tank_id'] or 'غير محدد'}")

    # آخر عمليات التوريد
    recent_supplies = chain_data.get('recent_supplies', [])
    if recent_supplies:
        st.subheader("آخر عمليات التوريد")
        for supply in recent_supplies[:3]:
            with st.expander(f"توريد {supply['invoice_no']} - {supply['date']}"):
                st.write(f"**المورد:** {supply['supplier']}")
                st.write(f"**الكمية:** {supply['quantity']} لتر")
                st.write(f"**السعر:** {supply['unit_price']} ريال/لتر")
                st.write(f"**الإجمالي:** {supply['total_amount']} ريال")

    # آخر المبيعات
    recent_sales = chain_data.get('recent_sales', [])
    if recent_sales:
        st.subheader("آخر المبيعات")
        for sale in recent_sales[:5]:
            st.write(f"• فاتورة {sale['invoice_no']}: {sale['fuel_amount']} لتر - {sale['total_price']} ريال - {sale['customer_name']}")

def display_supply_chain_optimization():
    """عرض تحسينات سلسلة التوريد في Streamlit"""
    st.subheader("🎯 تحسين سلسلة التوريد")

    optimization = supply_chain_integrator.optimize_supply_chain()

    if 'error' in optimization:
        st.error(optimization['error'])
        return

    recommendations = optimization.get('recommendations', [])

    if not recommendations:
        st.success("سلسلة التوريد في حالة جيدة - لا توجد توصيات فورية")
        return

    for rec in recommendations:
        if rec['type'] == 'critical':
            st.error(f"🚨 {rec['message']}")
        elif rec['type'] == 'warning':
            st.warning(f"⚠️ {rec['message']}")
        else:
            st.info(f"ℹ️ {rec['message']}")

        # أزرار الإجراءات
        if rec['action'] == 'schedule_emergency_supply':
            if st.button("جدولة توريد طارئ", key=f"emergency_{rec['type']}"):
                st.info("سيتم توجيهك لواجهة جدولة التوريد الطارئ")
        elif rec['action'] == 'schedule_supply':
            if st.button("جدولة توريد", key=f"supply_{rec['type']}"):
                st.info("سيتم توجيهك لواجهة جدولة التوريد")
        elif rec['action'] == 'assign_employees':
            if st.button("تعيين موظفين", key=f"assign_{rec['type']}"):
                st.info("سيتم توجيهك لواجهة تعيين الموظفين")

def predict_station_supply_needs(station_id: Optional[str] = None, days_ahead: int = 7):
    """توقع احتياجات التوريد للمحطة"""
    st.subheader("🔮 توقع احتياجات التوريد")

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
            selected_station = st.selectbox("اختر المحطة:", list(station_options.keys()), key="predict_station")
            station_id = station_options[selected_station]

        except Exception as e:
            st.error(f"خطأ في تحميل المحطات: {str(e)}")
            return

    prediction = supply_chain_integrator.predict_supply_needs(station_id, days_ahead)

    if 'error' in prediction:
        st.error(prediction['error'])
        return

    col1, col2 = st.columns(2)

    with col1:
        st.metric("الكمية الحالية", f"{prediction['current_amount']} لتر")
        st.metric("متوسط المبيعات اليومية", f"{prediction['avg_daily_sales']:.1f} لتر")
        st.metric("الاحتياجات المتوقعة", f"{prediction['required_amount']:.1f} لتر")

    with col2:
        st.metric("الأيام حتى النفاد", f"{prediction['days_until_empty']:.1f} يوم")
        supply_needed = prediction['supply_needed']
        st.metric("الكمية المطلوب توريدها", f"{supply_needed:.1f} لتر")

    # التوصية
    recommendation = prediction['recommendation']
    urgency = prediction['urgency']

    if recommendation == 'supply_needed':
        if urgency == 'high':
            st.error("🚨 يتطلب توريد فوري!")
        elif urgency == 'medium':
            st.warning("⚠️ يُنصح بالتوريد قريباً")
        else:
            st.info("ℹ️ يمكن جدولة التوريد")

        if st.button("إنشاء طلب توريد", use_container_width=True):
            st.success(f"تم إنشاء طلب توريد لكمية {supply_needed:.1f} لتر")
    else:
        st.success("✅ المخزون كافي للفترة المحددة")