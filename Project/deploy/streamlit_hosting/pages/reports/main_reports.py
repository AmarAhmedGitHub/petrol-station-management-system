import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
                SELECT Date, SUM(Total_Price) as Daily_Sales, COUNT(*) as Invoice_Count
                FROM Invoice
                WHERE Date BETWEEN %s AND %s
                GROUP BY Date
                ORDER BY Date
            """, (start_date, end_date))
        else:
            c.execute("""
                SELECT Date, SUM(Total_Price) as Daily_Sales, COUNT(*) as Invoice_Count
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
            SELECT Fuel_Type, SUM(Fuel_Amount) as Total_Fuel, AVG(Total_Price/Fuel_Amount) as Avg_Price_Per_Liter
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
                   SUM(i.Total_Price) as Total_Spent, AVG(i.Total_Price) as Avg_Purchase
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
        # Note: Invoice table may not contain Employee_ID in current schema.
        # Attempt to join if the column exists; otherwise return basic employee list with zeros.
        try:
            c.execute("""
                SELECT e.Emp_Name, e.Designation, COUNT(i.Invoice_No) as Invoices_Handled,
                       IFNULL(SUM(i.Total_Price),0) as Total_Sales, IFNULL(AVG(i.Total_Price),0) as Avg_Invoice
                FROM Employee e
                LEFT JOIN Invoice i ON e.Employee_ID = i.Employee_ID
                GROUP BY e.Employee_ID, e.Emp_Name, e.Designation
                ORDER BY Total_Sales DESC
            """)
            data = c.fetchall()
        except Exception:
            # Fallback: return employees without sales data
            c.execute("SELECT Emp_Name, Designation, Employee_ID FROM Employee")
            emp_rows = c.fetchall()
            data = []
            for r in emp_rows:
                # r could be dict or tuple
                if isinstance(r, dict):
                    data.append({'Emp_Name': r.get('Emp_Name'), 'Designation': r.get('Designation'), 'Invoices_Handled': 0, 'Total_Sales': 0, 'Avg_Invoice': 0})
                else:
                    data.append({'Emp_Name': r[0], 'Designation': r[1], 'Invoices_Handled': 0, 'Total_Sales': 0, 'Avg_Invoice': 0})

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
        st.rerun()

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
        st.rerun()

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
        st.rerun()

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
        st.rerun()

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
        st.rerun()

    # Get data
    sales_data = get_sales_report(start_date, end_date)

    if sales_data:
        # Normalize data (support both dict rows and tuple rows)
        if isinstance(sales_data, list) and len(sales_data) > 0 and isinstance(sales_data[0], dict):
            df = pd.DataFrame(sales_data)
        else:
            df = pd.DataFrame(sales_data, columns=['Date', 'Daily_Sales', 'Invoice_Count'])

        # Ensure Date is datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        # Rename to Arabic friendly columns for display
        rename_map = {}
        if 'Daily_Sales' in df.columns:
            rename_map['Daily_Sales'] = 'إجمالي المبيعات'
        if 'Invoice_Count' in df.columns:
            rename_map['Invoice_Count'] = 'عدد الفواتير'
        if 'Date' in df.columns:
            rename_map['Date'] = 'التاريخ'
        df_display = df.rename(columns=rename_map)

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 جدول المبيعات")

        # Summary statistics
        total_sales = df_display['إجمالي المبيعات'].sum()
        total_invoices = df_display['عدد الفواتير'].sum()
        avg_daily_sales = df_display['إجمالي المبيعات'].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي المبيعات", f"{total_sales:,.0f}")
        with col2:
            st.metric("إجمالي الفواتير", f"{total_invoices}")
        with col3:
            st.metric("متوسط المبيعات اليومية", f"{avg_daily_sales:.0f}")

        st.dataframe(df_display, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Interactive Chart with Plotly
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 رسم بياني للمبيعات (تفاعلي)")

        fig = px.line(df, x='Date', y='Daily_Sales', markers=True, title='اتجاه المبيعات اليومية')
        fig.update_layout(xaxis_title='التاريخ', yaxis_title='المبيعات')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_fuel_report():
    """Display fuel report"""
    st.markdown('<h2 class="section-header">⛽ تقرير الوقود</h2>', unsafe_allow_html=True)

    fuel_data = get_fuel_report()

    if fuel_data:
        if isinstance(fuel_data, list) and len(fuel_data) > 0 and isinstance(fuel_data[0], dict):
            df = pd.DataFrame(fuel_data)
        else:
            df = pd.DataFrame(fuel_data, columns=['Fuel_Type', 'Total_Fuel', 'Avg_Price_Per_Liter'])

        df_display = df.rename(columns={'Fuel_Type': 'نوع الوقود', 'Total_Fuel': 'إجمالي الكمية (لتر)', 'Avg_Price_Per_Liter': 'متوسط السعر للتر'})

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 تحليل استهلاك الوقود")

        # Summary statistics
        total_fuel = df_display['إجمالي الكمية (لتر)'].sum()
        most_popular = df_display.iloc[0]['نوع الوقود'] if len(df_display) > 0 else "لا توجد بيانات"

        col1, col2 = st.columns(2)
        with col1:
            st.metric("إجمالي الوقود المباع", f"{total_fuel:,.0f} لتر")
        with col2:
            st.metric("النوع الأكثر شعبية", most_popular)

        st.dataframe(df_display, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Interactive Pie/Donut chart with Plotly
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 توزيع أنواع الوقود")

        fig = px.pie(df_display, names='نوع الوقود', values='إجمالي الكمية (لتر)', title='توزيع استهلاك الوقود حسب النوع', hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_customer_report():
    """Display customer report"""
    st.markdown('<h2 class="section-header">👥 تقرير العملاء</h2>', unsafe_allow_html=True)

    customer_data = get_customer_report()

    if customer_data:
        if isinstance(customer_data, list) and len(customer_data) > 0 and isinstance(customer_data[0], dict):
            df = pd.DataFrame(customer_data)
        else:
            df = pd.DataFrame(customer_data, columns=['C_Name', 'City', 'Purchase_Count', 'Total_Spent', 'Avg_Purchase'])

        df_display = df.rename(columns={'C_Name': 'اسم العميل', 'City': 'المدينة', 'Purchase_Count': 'عدد المشتريات', 'Total_Spent': 'إجمالي الإنفاق', 'Avg_Purchase': 'متوسط المشتريات'})

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 أفضل 20 عميل")

        # Summary statistics
        total_customers = len(df_display)
        total_spent = df_display['إجمالي الإنفاق'].sum()
        avg_spent = df_display['إجمالي الإنفاق'].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي العملاء", f"{total_customers}")
        with col2:
            st.metric("إجمالي الإنفاق", f"{total_spent:,.0f}")
        with col3:
            st.metric("متوسط الإنفاق للعميل", f"{avg_spent:.0f}")

        st.dataframe(df_display, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Interactive Top customers bar chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 أكثر العملاء إنفاقاً")

        top_10 = df_display.head(10)
        fig = px.bar(top_10, x='اسم العميل', y='إجمالي الإنفاق', title='أكثر 10 عملاء إنفاقاً')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_employee_report():
    """Display employee performance report"""
    st.markdown('<h2 class="section-header">👨‍💼 تقرير أداء الموظفين</h2>', unsafe_allow_html=True)

    emp_data = get_employee_performance()

    if emp_data:
        if isinstance(emp_data, list) and len(emp_data) > 0 and isinstance(emp_data[0], dict):
            df = pd.DataFrame(emp_data)
        else:
            df = pd.DataFrame(emp_data, columns=['Emp_Name', 'Designation', 'Invoices_Handled', 'Total_Sales', 'Avg_Invoice'])

        df_display = df.rename(columns={'Emp_Name': 'اسم الموظف', 'Designation': 'المسمى الوظيفي', 'Invoices_Handled': 'عدد الفواتير', 'Total_Sales': 'إجمالي المبيعات', 'Avg_Invoice': 'متوسط الفاتورة'})

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 أداء الموظفين")

        # Summary statistics
        total_employees = len(df_display)
        total_invoices = df_display['عدد الفواتير'].sum()
        total_sales = df_display['إجمالي المبيعات'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي الموظفين", f"{total_employees}")
        with col2:
            st.metric("إجمالي الفواتير", f"{total_invoices}")
        with col3:
            st.metric("إجمالي المبيعات", f"{total_sales:,.0f}")

        st.dataframe(df_display, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Interactive bar chart for employee performance
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 مقارنة أداء الموظفين")

        fig = px.bar(df_display, x='اسم الموظف', y='إجمالي المبيعات', title='مقارنة إجمالي المبيعات بين الموظفين')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main reports function"""
    # Initialize session state
    if 'report_page' not in st.session_state:
        st.session_state.report_page = None

    # Navigation
    if st.session_state.report_page is None:
        show_reports_interface()
    elif st.session_state.report_page == "sales":
        show_sales_report()
        if st.button("⬅️ العودة للتقارير", key="back_to_reports"):
            st.session_state.report_page = None
            st.rerun()
    elif st.session_state.report_page == "fuel":
        show_fuel_report()
        if st.button("⬅️ العودة للتقارير", key="back_to_reports"):
            st.session_state.report_page = None
            st.rerun()
    elif st.session_state.report_page == "customer":
        show_customer_report()
        if st.button("⬅️ العودة للتقارير", key="back_to_reports"):
            st.session_state.report_page = None
            st.rerun()
    elif st.session_state.report_page == "employee":
        show_employee_report()
        if st.button("⬅️ العودة للتقارير", key="back_to_reports"):
            st.session_state.report_page = None
            st.rerun()

if __name__ == "__main__":
    main()
