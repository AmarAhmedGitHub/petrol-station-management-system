"""
محرك الإحصائيات المتقدم - Petrol Pump Management System
يوفر هذا النظام حسابات إحصائية محسنة مع فلاتر زمنية ومنطقية
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import pandas as pd
from database import get_connection
import streamlit as st

# إعداد نظام التسجيل
logging.basicConfig(
    filename='statistics_engine.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class StatisticsEngine:
    """محرك الإحصائيات المتقدم"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_timeout = 300  # 5 دقائق

    def get_date_filter_query(self, start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None,
                            date_column: str = 'Date') -> Tuple[str, tuple]:
        """
        إنشاء استعلام فلترة التواريخ

        Args:
            start_date: تاريخ البداية
            end_date: تاريخ النهاية
            date_column: اسم عمود التاريخ

        Returns:
            Tuple[str, tuple]: (الشرط, المعاملات)
        """
        conditions = []
        params = []

        if start_date:
            conditions.append(f"{date_column} >= %s")
            params.append(start_date)

        if end_date:
            conditions.append(f"{date_column} <= %s")
            params.append(end_date)

        if conditions:
            return " AND " + " AND ".join(conditions), tuple(params)
        return "", ()

    def get_sales_statistics(self, start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           group_by: str = 'day') -> Dict[str, Any]:
        """
        إحصائيات المبيعات مع فلاتر زمنية

        Args:
            start_date: تاريخ البداية
            end_date: تاريخ النهاية
            group_by: طريقة التجميع (day, week, month)

        Returns:
            Dict: إحصائيات المبيعات
        """
        try:
            conn = get_connection()
            if not conn:
                return {}

            c = conn.cursor()

            # فلترة التواريخ
            date_filter, date_params = self.get_date_filter_query(start_date, end_date)

            # إجمالي المبيعات
            c.execute(f"""
                SELECT
                    COALESCE(SUM(Total_Price), 0) as total_sales,
                    COALESCE(SUM(Fuel_Amount), 0) as total_fuel,
                    COUNT(*) as total_invoices,
                    COALESCE(AVG(Total_Price), 0) as avg_sale,
                    COALESCE(MIN(Total_Price), 0) as min_sale,
                    COALESCE(MAX(Total_Price), 0) as max_sale
                FROM Invoice
                WHERE 1=1 {date_filter}
            """, date_params)

            overall_stats = c.fetchone()

            # مبيعات حسب نوع الوقود
            c.execute(f"""
                SELECT
                    COALESCE(Fuel_Type_Actual, Fuel_Type) as fuel_type,
                    SUM(Fuel_Amount) as fuel_amount,
                    SUM(Total_Price) as revenue,
                    COUNT(*) as transactions,
                    AVG(Total_Price) as avg_price
                FROM Invoice
                WHERE 1=1 {date_filter}
                GROUP BY COALESCE(Fuel_Type_Actual, Fuel_Type)
                ORDER BY revenue DESC
            """, date_params)

            fuel_stats = c.fetchall()

            # مبيعات حسب الفترة الزمنية
            time_group = self._get_time_group_sql(group_by)
            c.execute(f"""
                SELECT
                    {time_group} as period,
                    SUM(Total_Price) as sales,
                    SUM(Fuel_Amount) as fuel_amount,
                    COUNT(*) as transactions,
                    AVG(Total_Price) as avg_sale
                FROM Invoice
                WHERE 1=1 {date_filter}
                GROUP BY {time_group}
                ORDER BY {time_group}
            """, date_params)

            time_stats = c.fetchall()

            # أفضل العملاء
            c.execute(f"""
                SELECT
                    i.Customer_Code,
                    c.C_Name,
                    COUNT(*) as transactions,
                    SUM(i.Total_Price) as total_spent,
                    AVG(i.Total_Price) as avg_transaction,
                    MAX(i.Date) as last_purchase
                FROM Invoice i
                JOIN Customer c ON i.Customer_Code = c.Customer_Code
                WHERE 1=1 {date_filter}
                GROUP BY i.Customer_Code, c.C_Name
                ORDER BY total_spent DESC
                LIMIT 10
            """, date_params)

            top_customers = c.fetchall()

            conn.close()

            return {
                'overall': {
                    'total_sales': overall_stats[0],
                    'total_fuel': overall_stats[1],
                    'total_invoices': overall_stats[2],
                    'avg_sale': overall_stats[3],
                    'min_sale': overall_stats[4],
                    'max_sale': overall_stats[5]
                },
                'by_fuel_type': [{
                    'fuel_type': row[0],
                    'fuel_amount': row[1],
                    'revenue': row[2],
                    'transactions': row[3],
                    'avg_price': row[4]
                } for row in fuel_stats],
                'by_time_period': [{
                    'period': row[0],
                    'sales': row[1],
                    'fuel_amount': row[2],
                    'transactions': row[3],
                    'avg_sale': row[4]
                } for row in time_stats],
                'top_customers': [{
                    'customer_code': row[0],
                    'customer_name': row[1],
                    'transactions': row[2],
                    'total_spent': row[3],
                    'avg_transaction': row[4],
                    'last_purchase': row[5]
                } for row in top_customers],
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'group_by': group_by
                }
            }

        except Exception as e:
            self.logger.error(f"Error calculating sales statistics: {str(e)}")
            return {}

    def get_inventory_statistics(self) -> Dict[str, Any]:
        """
        إحصائيات المخزون

        Returns:
            Dict: إحصائيات المخزون
        """
        try:
            conn = get_connection()
            if not conn:
                return {}

            c = conn.cursor()

            # إحصائيات الخزانات
            c.execute("""
                SELECT
                    COUNT(*) as total_tanks,
                    SUM(Capacity) as total_capacity,
                    SUM(Current_Amount) as total_current,
                    AVG(Current_Amount / Capacity * 100) as avg_fill_percentage,
                    SUM(CASE WHEN (Current_Amount / Capacity) <= 0.15 THEN 1 ELSE 0 END) as low_tanks,
                    SUM(CASE WHEN (Current_Amount / Capacity) <= 0.30 THEN 1 ELSE 0 END) as medium_low_tanks
                FROM FuelTank
            """)

            tank_stats = c.fetchone()

            # حركة المخزون في آخر 30 يوم
            thirty_days_ago = datetime.now() - timedelta(days=30)
            c.execute("""
                SELECT
                    Transaction_Type,
                    SUM(Amount) as total_amount,
                    COUNT(*) as transaction_count
                FROM InventoryTransactions
                WHERE Transaction_Date >= %s
                GROUP BY Transaction_Type
            """, (thirty_days_ago,))

            movement_stats = dict(c.fetchall())

            # تنبيهات المخزون النشطة
            c.execute("""
                SELECT
                    COUNT(*) as active_alerts,
                    SUM(CASE WHEN Severity = 'CRITICAL' THEN 1 ELSE 0 END) as critical_alerts,
                    SUM(CASE WHEN Severity = 'HIGH' THEN 1 ELSE 0 END) as high_alerts
                FROM InventoryAlerts
                WHERE Resolved = FALSE
            """)

            alert_stats = c.fetchone()

            conn.close()

            return {
                'tanks': {
                    'total_tanks': tank_stats[0],
                    'total_capacity': tank_stats[1],
                    'total_current': tank_stats[2],
                    'avg_fill_percentage': tank_stats[3],
                    'low_tanks': tank_stats[4],
                    'medium_low_tanks': tank_stats[5]
                },
                'movement_30_days': movement_stats,
                'alerts': {
                    'active_alerts': alert_stats[0],
                    'critical_alerts': alert_stats[1],
                    'high_alerts': alert_stats[2]
                }
            }

        except Exception as e:
            self.logger.error(f"Error calculating inventory statistics: {str(e)}")
            return {}

    def get_employee_performance_stats(self, start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        إحصائيات أداء الموظفين

        Args:
            start_date: تاريخ البداية
            end_date: تاريخ النهاية

        Returns:
            Dict: إحصائيات أداء الموظفين
        """
        try:
            conn = get_connection()
            if not conn:
                return {}

            c = conn.cursor()

            date_filter, date_params = self.get_date_filter_query(start_date, end_date)

            # أداء الموظفين في المبيعات
            c.execute(f"""
                SELECT
                    e.Employee_ID,
                    e.Emp_Name,
                    COUNT(i.Invoice_No) as total_invoices,
                    COALESCE(SUM(i.Total_Price), 0) as total_sales,
                    COALESCE(SUM(i.Fuel_Amount), 0) as total_fuel_sold,
                    COALESCE(AVG(i.Total_Price), 0) as avg_sale,
                    COUNT(DISTINCT i.Customer_Code) as unique_customers
                FROM Employee e
                LEFT JOIN Invoice i ON e.Employee_ID = i.Employee_ID
                WHERE 1=1 {date_filter}
                GROUP BY e.Employee_ID, e.Emp_Name
                ORDER BY total_sales DESC
            """, date_params)

            employee_sales = c.fetchall()

            # ديون الموظفين
            c.execute("""
                SELECT
                    e.Employee_ID,
                    e.Emp_Name,
                    COUNT(ed.Debt_ID) as total_debts,
                    COALESCE(SUM(ed.Owed_Amount), 0) as total_owed,
                    COALESCE(SUM(CASE WHEN ed.Status = 'Pending' THEN ed.Owed_Amount ELSE 0 END), 0) as pending_amount,
                    COUNT(CASE WHEN ed.Status = 'Paid' THEN 1 END) as paid_debts
                FROM Employee e
                LEFT JOIN EmployeeDebt ed ON e.Employee_ID = ed.Employee_ID
                GROUP BY e.Employee_ID, e.Emp_Name
                ORDER BY total_owed DESC
            """)

            employee_debts = c.fetchall()

            conn.close()

            return {
                'sales_performance': [{
                    'employee_id': row[0],
                    'employee_name': row[1],
                    'total_invoices': row[2],
                    'total_sales': row[3],
                    'total_fuel_sold': row[4],
                    'avg_sale': row[5],
                    'unique_customers': row[6]
                } for row in employee_sales],
                'debt_summary': [{
                    'employee_id': row[0],
                    'employee_name': row[1],
                    'total_debts': row[2],
                    'total_owed': row[3],
                    'pending_amount': row[4],
                    'paid_debts': row[5]
                } for row in employee_debts],
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }

        except Exception as e:
            self.logger.error(f"Error calculating employee performance stats: {str(e)}")
            return {}

    def get_financial_summary(self, start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        ملخص مالي شامل

        Args:
            start_date: تاريخ البداية
            end_date: تاريخ النهاية

        Returns:
            Dict: الملخص المالي
        """
        try:
            conn = get_connection()
            if not conn:
                return {}

            c = conn.cursor()

            date_filter, date_params = self.get_date_filter_query(start_date, end_date)

            # إيرادات المبيعات
            c.execute(f"""
                SELECT
                    COALESCE(SUM(Total_Price), 0) as total_revenue,
                    COALESCE(SUM(Discount), 0) as total_discounts,
                    COUNT(*) as total_transactions
                FROM Invoice
                WHERE 1=1 {date_filter}
            """, date_params)

            revenue_stats = c.fetchone()

            # مصروفات التوريد
            c.execute(f"""
                SELECT
                    COALESCE(SUM(Total_Amount), 0) as total_supply_cost,
                    COALESCE(SUM(Quantity), 0) as total_fuel_supplied,
                    COUNT(*) as total_supply_transactions
                FROM FuelSupply
                WHERE 1=1 {date_filter.replace('Date', 'Supply_Date')}
            """, date_params)

            supply_stats = c.fetchone()

            # رواتب الموظفين
            c.execute(f"""
                SELECT
                    COUNT(DISTINCT e.Employee_ID) as total_employees,
                    COALESCE(SUM(e.Salary), 0) as total_salaries
                FROM Employee e
                WHERE e.DOB <= CURDATE() - INTERVAL 18 YEAR
            """)

            salary_stats = c.fetchone()

            # ديون الموظفين
            c.execute("""
                SELECT
                    COALESCE(SUM(Owed_Amount), 0) as total_debts,
                    COALESCE(SUM(CASE WHEN Status = 'Pending' THEN Owed_Amount ELSE 0 END), 0) as pending_debts
                FROM EmployeeDebt
            """)

            debt_stats = c.fetchone()

            conn.close()

            # حساب الأرباح والخسائر
            total_revenue = revenue_stats[0]
            total_discounts = revenue_stats[1]
            net_revenue = total_revenue - total_discounts

            total_costs = supply_stats[0] + salary_stats[1] + debt_stats[0]
            net_profit = net_revenue - total_costs

            return {
                'revenue': {
                    'gross_revenue': total_revenue,
                    'total_discounts': total_discounts,
                    'net_revenue': net_revenue,
                    'total_transactions': revenue_stats[2]
                },
                'costs': {
                    'supply_costs': supply_stats[0],
                    'fuel_supplied': supply_stats[1],
                    'supply_transactions': supply_stats[2],
                    'employee_salaries': salary_stats[1],
                    'total_employees': salary_stats[0],
                    'employee_debts': debt_stats[0],
                    'pending_debts': debt_stats[1],
                    'total_costs': total_costs
                },
                'profitability': {
                    'net_profit': net_profit,
                    'profit_margin': (net_profit / net_revenue * 100) if net_revenue > 0 else 0,
                    'revenue_per_employee': net_revenue / salary_stats[0] if salary_stats[0] > 0 else 0
                },
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }

        except Exception as e:
            self.logger.error(f"Error calculating financial summary: {str(e)}")
            return {}

    def _get_time_group_sql(self, group_by: str) -> str:
        """إنشاء SQL للتجميع الزمني"""
        if group_by == 'day':
            return "DATE(Date)"
        elif group_by == 'week':
            return "YEARWEEK(Date)"
        elif group_by == 'month':
            return "DATE_FORMAT(Date, '%Y-%m')"
        elif group_by == 'quarter':
            return "CONCAT(YEAR(Date), '-Q', QUARTER(Date))"
        elif group_by == 'year':
            return "YEAR(Date)"
        else:
            return "DATE(Date)"

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        مقاييس لوحة التحكم الرئيسية

        Returns:
            Dict: المقاييس
        """
        # إحصائيات اليوم
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())

        sales_today = self.get_sales_statistics(start_date=today_start, end_date=datetime.now())
        inventory_stats = self.get_inventory_statistics()

        return {
            'today_sales': sales_today.get('overall', {}),
            'inventory_status': inventory_stats,
            'alerts_count': inventory_stats.get('alerts', {}).get('active_alerts', 0),
            'low_stock_tanks': inventory_stats.get('tanks', {}).get('low_tanks', 0)
        }

# إنشاء instance عالمي
statistics_engine = StatisticsEngine()

# دوال مساعدة للاستخدام في Streamlit
def display_sales_statistics(start_date=None, end_date=None, group_by='day'):
    """عرض إحصائيات المبيعات في Streamlit"""
    st.subheader("📊 إحصائيات المبيعات")

    stats = statistics_engine.get_sales_statistics(start_date, end_date, group_by)

    if not stats:
        st.error("فشل في تحميل إحصائيات المبيعات")
        return

    overall = stats['overall']

    # المقاييس الرئيسية
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("إجمالي المبيعات", f"{overall['total_sales']:,.0f} ريال")
    with col2:
        st.metric("إجمالي الوقود", f"{overall['total_fuel']:,.0f} لتر")
    with col3:
        st.metric("عدد الفواتير", overall['total_invoices'])
    with col4:
        st.metric("متوسط الفاتورة", f"{overall['avg_sale']:,.0f} ريال")

    # مبيعات حسب نوع الوقود
    if stats['by_fuel_type']:
        st.subheader("مبيعات حسب نوع الوقود")
        fuel_df = pd.DataFrame(stats['by_fuel_type'])
        st.bar_chart(fuel_df.set_index('fuel_type')['revenue'])

    # أفضل العملاء
    if stats['top_customers']:
        st.subheader("أفضل العملاء")
        customers_df = pd.DataFrame(stats['top_customers'][:5])
        st.dataframe(customers_df[['customer_name', 'total_spent', 'transactions']])

def display_inventory_statistics():
    """عرض إحصائيات المخزون في Streamlit"""
    st.subheader("📦 إحصائيات المخزون")

    stats = statistics_engine.get_inventory_statistics()

    if not stats:
        st.error("فشل في تحميل إحصائيات المخزون")
        return

    tanks = stats['tanks']

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("عدد الخزانات", tanks['total_tanks'])
    with col2:
        st.metric("السعة الكلية", f"{tanks['total_capacity']:,.0f} لتر")
    with col3:
        st.metric("الكمية الحالية", f"{tanks['total_current']:,.0f} لتر")
    with col4:
        st.metric("متوسط التعبئة", f"{tanks['avg_fill_percentage']:.1f}%")

    # تنبيهات المخزون
    alerts = stats['alerts']
    if alerts['active_alerts'] > 0:
        st.warning(f"⚠️ يوجد {alerts['active_alerts']} تنبيه مخزون نشط")
        if alerts['critical_alerts'] > 0:
            st.error(f"🚨 {alerts['critical_alerts']} تنبيه حرج")

def display_financial_summary(start_date=None, end_date=None):
    """عرض الملخص المالي في Streamlit"""
    st.subheader("💰 الملخص المالي")

    stats = statistics_engine.get_financial_summary(start_date, end_date)

    if not stats:
        st.error("فشل في تحميل الملخص المالي")
        return

    revenue = stats['revenue']
    costs = stats['costs']
    profitability = stats['profitability']

    # الإيرادات
    st.subheader("الإيرادات")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("إجمالي الإيرادات", f"{revenue['gross_revenue']:,.0f} ريال")
    with col2:
        st.metric("إجمالي الخصومات", f"{revenue['total_discounts']:,.0f} ريال")
    with col3:
        st.metric("صافي الإيرادات", f"{revenue['net_revenue']:,.0f} ريال")

    # التكاليف
    st.subheader("التكاليف")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("تكلفة التوريد", f"{costs['supply_costs']:,.0f} ريال")
    with col2:
        st.metric("رواتب الموظفين", f"{costs['employee_salaries']:,.0f} ريال")
    with col3:
        st.metric("ديون الموظفين", f"{costs['employee_debts']:,.0f} ريال")
    with col4:
        st.metric("إجمالي التكاليف", f"{costs['total_costs']:,.0f} ريال")

    # الربحية
    st.subheader("الربحية")
    col1, col2, col3 = st.columns(3)
    with col1:
        profit_color = "inverse" if profitability['net_profit'] < 0 else "normal"
        st.metric("صافي الربح", f"{profitability['net_profit']:,.0f} ريال", delta_color=profit_color)
    with col2:
        st.metric("هامش الربح", f"{profitability['profit_margin']:.1f}%")
    with col3:
        st.metric("الإيراد لكل موظف", f"{profitability['revenue_per_employee']:,.0f} ريال")

def display_employee_performance(start_date=None, end_date=None):
    """عرض أداء الموظفين في Streamlit"""
    st.subheader("👥 أداء الموظفين")

    stats = statistics_engine.get_employee_performance_stats(start_date, end_date)

    if not stats:
        st.error("فشل في تحميل إحصائيات الأداء")
        return

    # أداء المبيعات
    if stats['sales_performance']:
        st.subheader("أداء المبيعات")
        sales_df = pd.DataFrame(stats['sales_performance'])
        st.dataframe(sales_df[['employee_name', 'total_sales', 'total_invoices', 'avg_sale']])

        # رسم بياني للمبيعات
        st.bar_chart(sales_df.set_index('employee_name')['total_sales'])

    # ملخص الديون
    if stats['debt_summary']:
        st.subheader("ملخص الديون")
        debt_df = pd.DataFrame(stats['debt_summary'])
        st.dataframe(debt_df[['employee_name', 'total_owed', 'pending_amount', 'total_debts']])