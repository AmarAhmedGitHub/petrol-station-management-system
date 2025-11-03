import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from core.database import get_connection
import datetime

def get_sales_report(start_date=None, end_date=None):
    """Get sales report data"""
    conn = get_connection()
    if not conn:
        return None

    c = conn.cursor()

    try:
        if start_date and end_date:
            c.execute("""
                SELECT Date, IFNULL(SUM(Total_Price), 0) as Daily_Sales, COUNT(*) as Invoice_Count
                FROM Invoice
                WHERE Date BETWEEN %s AND %s
                GROUP BY Date
                ORDER BY Date
            """, (start_date, end_date))
        else:
            c.execute("""
                SELECT Date, IFNULL(SUM(Total_Price), 0) as Daily_Sales, COUNT(*) as Invoice_Count
                FROM Invoice
                GROUP BY Date
                ORDER BY Date
            """)

        data = c.fetchall()
        conn.close()
        return data
    except Exception as e:
        st.error(f"خطأ في جلب تقرير المبيعات: {e}")
        conn.close()
        return None

def get_fuel_report():
    """Get fuel consumption report"""
    conn = get_connection()
    if not conn:
        return None

    c = conn.cursor()

    try:
        c.execute("""
            SELECT Fuel_Type, IFNULL(SUM(Fuel_Amount), 0) as Total_Fuel, IFNULL(AVG(Total_Price/Fuel_Amount), 0) as Avg_Price_Per_Liter
            FROM Invoice
            WHERE Fuel_Amount > 0
            GROUP BY Fuel_Type
            ORDER BY Total_Fuel DESC
        """)

        data = c.fetchall()
        conn.close()
        return data
    except Exception as e:
        st.error(f"خطأ في جلب تقرير الوقود: {e}")
        conn.close()
        return None

def get_customer_report():
    """Get customer analysis report"""
    conn = get_connection()
    if not conn:
        return None

    c = conn.cursor()

    try:
        c.execute("""
            SELECT c.C_Name, c.City, COUNT(i.Invoice_No) as Purchase_Count,
                   IFNULL(SUM(i.Total_Price), 0) as Total_Spent, IFNULL(AVG(i.Total_Price), 0) as Avg_Purchase
            FROM Customer c
            LEFT JOIN Invoice i ON c.Customer_Code = i.Customer_Code
            GROUP BY c.Customer_Code, c.C_Name, c.City
            ORDER BY Total_Spent DESC
            LIMIT 20
        """)

        data = c.fetchall()
        conn.close()
        return data
    except Exception as e:
        st.error(f"خطأ في جلب تقرير العملاء: {e}")
        conn.close()
        return None

def get_employee_performance():
    """Get employee performance report"""
    conn = get_connection()
    if not conn:
        return None

    c = conn.cursor()

    try:
        c.execute("""
            SELECT e.Emp_Name, e.Designation, COUNT(i.Invoice_No) as Invoices_Handled,
                   IFNULL(SUM(i.Total_Price), 0) as Total_Sales, IFNULL(AVG(i.Total_Price), 0) as Avg_Invoice
            FROM Employee e
            LEFT JOIN Invoice i ON e.Employee_ID = i.Invoice_No
            GROUP BY e.Employee_ID, e.Emp_Name, e.Designation
            ORDER BY Total_Sales DESC
        """)

        data = c.fetchall()
        conn.close()
        return data
    except Exception as e:
        st.error(f"خطأ في جلب تقرير أداء الموظفين: {e}")
        conn.close()
        return None

def show_reports_interface():
    """Display main reports interface"""
    st.markdown("""
        <style>
        .reports-container {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
        }
        .reports-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .report-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .report-card:hover {
            transform: translateY(-5px);
            border-color: #28a745;
            box-shadow: 0 8px 25px rgba(40,167,69,0.2);
        }
        .report-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .report-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #28a745;
            margin-bottom: 1rem;
        }
        .report-description {
            color: #6c757d;
            margin-bottom: 1.5rem;
        }
        .report-button {
            background: linear-gradient(45deg, #28a745, #20c997) !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 0.75rem 2rem !important;
            font-size: 1rem !important;
            font-weight: bold !important;
            width: 100% !important;
            margin-top: 1rem !important;
        }
        .section-header {
            color: #28a745;
            font-size: 2rem;
            font-weight: bold;
            margin: 2rem 0 1rem 0;
            text-align: center;
        }
        .chart-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin: 2rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="section-header">📊 التقارير والإحصائيات</h1>', unsafe_allow_html=True)

    st.markdown('<div class="reports-grid">', unsafe_allow_html=True)

    # Sales Report
    st.markdown('''
        <div class="report-card">
            <div class="report-icon">💰</div>
            <div class="report-title">تقرير المبيعات</div>
            <div class="report-description">
                تحليل المبيعات اليومية والشهرية مع الرسوم البيانية
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("📈 تقرير المبيعات", key="sales_report", use_container_width=True):
        st.session_state.report_page = "sales"
        st.session_state.previous_page = st.session_state.current_page
        st.session_state.current_page = 'reports'

    # Fuel Report
    st.markdown('''
        <div class="report-card">
            <div class="report-icon">⛽</div>
            <div class="report-title">تقرير الوقود</div>
            <div class="report-description">
                تحليل استهلاك الوقود وتوزيع الأنواع المختلفة
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("⛽ تقرير الوقود", key="fuel_report", use_container_width=True):
        st.session_state.report_page = "fuel"
        st.session_state.previous_page = st.session_state.current_page
        st.session_state.current_page = 'reports'

    # Customer Report
    st.markdown('''
        <div class="report-card">
            <div class="report-icon">👥</div>
            <div class="report-title">تقرير العملاء</div>
            <div class="report-description">
                تحليل سلوك العملاء وأكثرهم إنفاقاً
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("👥 تقرير العملاء", key="customer_report", use_container_width=True):
        st.session_state.report_page = "customer"
        st.session_state.previous_page = st.session_state.current_page
        st.session_state.current_page = 'reports'

    # Employee Performance
    st.markdown('''
        <div class="report-card">
            <div class="report-icon">👨‍💼</div>
            <div class="report-title">أداء الموظفين</div>
            <div class="report-description">
                تقييم أداء الموظفين وإحصائيات المبيعات
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("👨‍💼 أداء الموظفين", key="employee_report", use_container_width=True):
        st.session_state.report_page = "employee"
        st.session_state.previous_page = st.session_state.current_page
        st.session_state.current_page = 'reports'

    st.markdown('</div>', unsafe_allow_html=True)

def show_sales_report():
    """Display sales report"""
    st.markdown('<h2 class="section-header">💰 تقرير المبيعات</h2>', unsafe_allow_html=True)

    # Date filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("تاريخ البداية", datetime.date.today() - datetime.timedelta(days=30))
    with col2:
        end_date = st.date_input("تاريخ النهاية", datetime.date.today())

    if st.button("🔍 تطبيق التصفية", key="apply_filter"):
        st.session_state.report_filter_applied = True

    # Get data
    sales_data = get_sales_report(start_date, end_date)

    if sales_data:
        df = pd.DataFrame(sales_data, columns=['التاريخ', 'إجمالي المبيعات', 'عدد الفواتير'])

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 جدول المبيعات")

        # Summary statistics
        total_sales = df['إجمالي المبيعات'].sum()
        total_invoices = df['عدد الفواتير'].sum()
        avg_daily_sales = df['إجمالي المبيعات'].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي المبيعات", f"{total_sales:,.0f}")
        with col2:
            st.metric("إجمالي الفواتير", f"{total_invoices}")
        with col3:
            st.metric("متوسط المبيعات اليومية", f"{avg_daily_sales:.0f}")

        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 رسم بياني للمبيعات")

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df['التاريخ'], df['إجمالي المبيعات'], marker='o', linewidth=2, markersize=6)
        ax.set_title('اتجاه المبيعات اليومية')
        ax.set_xlabel('التاريخ')
        ax.set_ylabel('المبيعات')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)

def show_fuel_report():
    """Display fuel report"""
    st.markdown('<h2 class="section-header">⛽ تقرير الوقود</h2>', unsafe_allow_html=True)

    fuel_data = get_fuel_report()

    if fuel_data:
        df = pd.DataFrame(fuel_data, columns=['نوع الوقود', 'إجمالي الكمية (لتر)', 'متوسط السعر للتر'])

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 تحليل استهلاك الوقود")

        # Summary statistics
        total_fuel = df['إجمالي الكمية (لتر)'].sum()
        most_popular = df.iloc[0]['نوع الوقود'] if len(df) > 0 else "لا توجد بيانات"

        col1, col2 = st.columns(2)
        with col1:
            st.metric("إجمالي الوقود المباع", f"{total_fuel:,.0f} لتر")
        with col2:
            st.metric("النوع الأكثر شعبية", most_popular)

        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Pie chart for fuel types
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 توزيع أنواع الوقود")

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.pie(df['إجمالي الكمية (لتر)'], labels=df['نوع الوقود'], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        ax.set_title('توزيع استهلاك الوقود حسب النوع')
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)

def show_customer_report():
    """Display customer report"""
    st.markdown('<h2 class="section-header">👥 تقرير العملاء</h2>', unsafe_allow_html=True)

    customer_data = get_customer_report()

    if customer_data:
        df = pd.DataFrame(customer_data, columns=['اسم العميل', 'المدينة', 'عدد المشتريات', 'إجمالي الإنفاق', 'متوسط المشتريات'])

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 أفضل 20 عميل")

        # Summary statistics
        total_customers = len(df)
        total_spent = df['إجمالي الإنفاق'].sum()
        avg_spent = df['إجمالي الإنفاق'].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي العملاء", f"{total_customers}")
        with col2:
            st.metric("إجمالي الإنفاق", f"{total_spent:,.0f}")
        with col3:
            st.metric("متوسط الإنفاق للعميل", f"{avg_spent:.0f}")

        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Top customers chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 أكثر العملاء إنفاقاً")

        top_10 = df.head(10)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(top_10['اسم العميل'], top_10['إجمالي الإنفاق'])
        ax.set_title('أكثر 10 عملاء إنفاقاً')
        ax.set_xlabel('اسم العميل')
        ax.set_ylabel('إجمالي الإنفاق')
        plt.xticks(rotation=45)
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)

def show_employee_report():
    """Display employee performance report"""
    st.markdown('<h2 class="section-header">👨‍💼 تقرير أداء الموظفين</h2>', unsafe_allow_html=True)

    emp_data = get_employee_performance()

    if emp_data:
        df = pd.DataFrame(emp_data, columns=['اسم الموظف', 'المسمى الوظيفي', 'عدد الفواتير', 'إجمالي المبيعات', 'متوسط الفاتورة'])

        # Clean data - ensure no None values
        df = df.fillna(0)
        df['إجمالي المبيعات'] = pd.to_numeric(df['إجمالي المبيعات'], errors='coerce').fillna(0)
        df['عدد الفواتير'] = pd.to_numeric(df['عدد الفواتير'], errors='coerce').fillna(0)

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 أداء الموظفين")

        # Summary statistics
        total_employees = len(df)
        total_invoices = int(df['عدد الفواتير'].sum())
        total_sales = float(df['إجمالي المبيعات'].sum())

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي الموظفين", f"{total_employees}")
        with col2:
            st.metric("إجمالي الفواتير", f"{total_invoices}")
        with col3:
            st.metric("إجمالي المبيعات", f"{total_sales:,.0f}")

        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Performance chart - only show employees with sales > 0
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 مقارنة أداء الموظفين")

        # Filter employees with actual sales
        df_with_sales = df[df['إجمالي المبيعات'] > 0]

        if len(df_with_sales) > 0:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.bar(df_with_sales['اسم الموظف'], df_with_sales['إجمالي المبيعات'])
            ax.set_title('مقارنة إجمالي المبيعات بين الموظفين')
            ax.set_xlabel('اسم الموظف')
            ax.set_ylabel('إجمالي المبيعات')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.info("لا توجد مبيعات مسجلة للموظفين حتى الآن")

        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main reports function"""
    # Initialize session state
    if 'report_page' not in st.session_state:
        st.session_state.report_page = None
    if 'previous_page' not in st.session_state:
        st.session_state.previous_page = 'dashboard'

    # Navigation
    if st.session_state.report_page is None:
        show_reports_interface()
    elif st.session_state.report_page == "sales":
        show_sales_report()
        if st.button("⬅️ العودة للتقارير", key="back_to_reports"):
            st.session_state.report_page = None
            st.session_state.current_page = st.session_state.previous_page
            # Don't use st.rerun() - let the main app handle navigation
    elif st.session_state.report_page == "fuel":
        show_fuel_report()
        if st.button("⬅️ العودة للتقارير", key="back_to_reports"):
            st.session_state.report_page = None
            st.session_state.current_page = st.session_state.previous_page
            # Don't use st.rerun() - let the main app handle navigation
    elif st.session_state.report_page == "customer":
        show_customer_report()
        if st.button("⬅️ العودة للتقارير", key="back_to_reports"):
            st.session_state.report_page = None
            st.session_state.current_page = st.session_state.previous_page
            # Don't use st.rerun() - let the main app handle navigation
    elif st.session_state.report_page == "employee":
        show_employee_report()
        if st.button("⬅️ العودة للتقارير", key="back_to_reports"):
            st.session_state.report_page = None
            st.session_state.current_page = st.session_state.previous_page
            # Don't use st.rerun() - let the main app handle navigation

if __name__ == "__main__":
    main()
