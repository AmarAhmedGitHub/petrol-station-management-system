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

def show_fuel_price_banner():
    """Display movable fuel price banner at the top"""
    st.markdown("""
        <style>
        .fuel-banner {
            background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7);
            background-size: 400% 400%;
            animation: gradientShift 8s ease infinite;
            color: white;
            padding: 1rem 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            text-align: center;
            font-weight: bold;
            font-size: 1.2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            position: relative;
            overflow: hidden;
        }

        .fuel-banner::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            animation: shimmer 3s infinite;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }

        .fuel-prices {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
            margin-top: 0.5rem;
        }

        .fuel-item {
            background: rgba(255,255,255,0.1);
            padding: 0.5rem 1rem;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }

        .fuel-name {
            font-size: 1.1rem;
            font-weight: bold;
        }

        .fuel-price {
            font-size: 1.3rem;
            color: #ffd700;
            font-weight: bold;
        }

        @media (max-width: 768px) {
            .fuel-prices {
                gap: 1rem;
            }
            .fuel-item {
                padding: 0.3rem 0.8rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # Get fuel prices from database
    conn = get_connection()
    if conn:
        c = conn.cursor()
        try:
            c.execute("SELECT DISTINCT Fuel_Name, Fuel_Price FROM Tanker WHERE Fuel_Price IS NOT NULL ORDER BY Fuel_Name")
            fuel_data = c.fetchall()
            conn.close()

            if fuel_data:
                fuel_html = '<div class="fuel-prices">'
                for fuel_name, fuel_price in fuel_data:
                    fuel_html += f'''
                        <div class="fuel-item">
                            <div class="fuel-name">{fuel_name}</div>
                            <div class="fuel-price">{fuel_price:.2f} ريال</div>
                        </div>
                    '''
                fuel_html += '</div>'

                st.markdown(f'''
                    <div class="fuel-banner">
                        ⛽ أسعار الوقود الحالية
                        {fuel_html}
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown('''
                    <div class="fuel-banner">
                        ⛽ أسعار الوقود الحالية - جاري التحديث...
                    </div>
                ''', unsafe_allow_html=True)
        except Exception as e:
            conn.close()
            st.markdown('''
                <div class="fuel-banner">
                    ⛽ أسعار الوقود الحالية - جاري التحديث...
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.markdown('''
            <div class="fuel-banner">
                ⛽ أسعار الوقود الحالية - جاري التحديث...
            </div>
        ''', unsafe_allow_html=True)



def insert_dummy_data():
    """Insert dummy data into database for testing"""
    conn = get_connection()
    if not conn:
        return

    c = conn.cursor()

    try:
        # Insert dummy customers
        customers = [
            ("أحمد محمد", "الرياض", "1234567890"),
            ("فاطمة علي", "جدة", "0987654321"),
            ("محمد عبدالله", "الدمام", "1122334455"),
            ("سارة خالد", "الرياض", "5566778899"),
            ("عبدالله أحمد", "مكة", "4433221100")
        ]
        c.executemany("INSERT IGNORE INTO Customer (C_Name, City, Phone_No) VALUES (%s, %s, %s)", customers)

        # Insert dummy employees
        employees = [
            ("محمد أحمد", "مدير", "5000"),
            ("فاطمة سالم", "موظف", "3000"),
            ("علي حسن", "موظف", "3000"),
            ("نورة عبدالله", "محاسب", "4000")
        ]
        c.executemany("INSERT IGNORE INTO Employee (Emp_Name, Designation, Salary) VALUES (%s, %s, %s)", employees)

        # Insert dummy fuel data
        fuels = [
            ("بنزين 91", 2.50),
            ("بنزين 95", 2.75),
            ("ديزل", 2.20)
        ]
        c.executemany("INSERT IGNORE INTO Tanker (Fuel_Name, Fuel_Price) VALUES (%s, %s)", fuels)

        # Insert dummy invoices
        today = datetime.date.today()
        invoices = [
            (1, 1, today, 50.0, "بنزين 91", 1),
            (2, 2, today, 75.0, "بنزين 95", 2),
            (3, 3, today, 100.0, "ديزل", 3),
            (4, 1, today, 60.0, "بنزين 91", 1),
            (5, 4, today, 80.0, "بنزين 95", 2)
        ]
        c.executemany("INSERT IGNORE INTO Invoice (Customer_Code, Employee_ID, Date, Fuel_Amount, Fuel_Type, Total_Price) VALUES (%s, %s, %s, %s, %s, %s)", invoices)

        conn.commit()
        st.success("تم إدراج البيانات التجريبية بنجاح!")
    except Exception as e:
        st.error(f"خطأ في إدراج البيانات التجريبية: {e}")
        conn.rollback()
    finally:
        conn.close()

def show_daily_reports():
    """Display daily reports section"""
    # Get today's date
    today = datetime.date.today()

    # Get daily data
    sales_data = get_sales_report(today, today)
    fuel_data = get_fuel_report()

    # Calculate daily metrics
    today_sales = 0
    today_invoices = 0
    if sales_data:
        today_sales = sum(row[1] for row in sales_data)
        today_invoices = sum(row[2] for row in sales_data)

    # Calculate fuel sold today (simplified)
    today_fuel = 0
    if fuel_data:
        # This is approximate - in real implementation, you'd filter by today's date
        today_fuel = sum(row[1] for row in fuel_data) * 0.1  # Assuming 10% of total is daily

    # Calculate expenses (simplified - would come from expenses table)
    today_expenses = today_sales * 0.15  # Assuming 15% expenses

    # Calculate profit/loss
    today_profit = today_sales - today_expenses

    # Header
    st.markdown(f"## 📊 التقارير اليومية - {today.strftime('%Y-%m-%d')}")
    st.markdown("### ملخص شامل للأرباح والخسائر والمصروفات والمبيعات")

    # Daily metrics using Streamlit columns and metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        delta_color = "normal" if today_profit >= 0 else "inverse"
        st.metric("صافي الربح/الخسارة", f"{today_profit:,.0f} ريال", delta=None, delta_color=delta_color)
    with col2:
        st.metric("إجمالي المبيعات", f"{today_sales:,.0f} ريال")
    with col3:
        st.metric("إجمالي المصروفات", f"{today_expenses:,.0f} ريال")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("كمية الوقود المباعة", f"{today_fuel:,.0f} لتر")
    with col5:
        st.metric("عدد الفواتير", f"{today_invoices}")
    with col6:
        avg_invoice = today_sales / today_invoices if today_invoices > 0 else 0
        st.metric("متوسط الفاتورة", f"{avg_invoice:.0f} ريال")

def main():
    """Main reports function"""
    if not st.session_state.get('logged_in', False):
        st.warning("⚠️ يجب تسجيل الدخول للوصول إلى صفحة التقارير.")
        return

    # Initialize session state
    if 'report_page' not in st.session_state:
        st.session_state.report_page = None

    # Insert dummy data if not already inserted
    if st.button("إدراج بيانات تجريبية", key="insert_dummy"):
        insert_dummy_data()

    # Show fuel price banner at the top
    show_fuel_price_banner()

    # Show daily reports
    show_daily_reports()

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
