import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from core.database_enhanced import (
    get_all_invoices, add_invoice, get_all_stations, get_all_pumps,
    get_all_tanks, get_all_fuel_types, get_all_employees, get_all_customers
)

def main():
    """Main management page for invoices"""

    st.title("🧾 إدارة الفواتير")

    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs([
        "➕ إنشاء فاتورة",
        "📋 جميع الفواتير",
        "📊 تقارير الفواتير"
    ])

    with tab1:
        create_invoice_tab()

    with tab2:
        view_invoices_tab()

    with tab3:
        invoices_reports_tab()

def create_invoice_tab():
    """Create new invoice"""
    st.subheader("➕ إنشاء فاتورة جديدة")

    # Get data for dropdowns
    stations = get_all_stations()
    pumps = get_all_pumps()
    tanks = get_all_tanks()
    fuel_types = get_all_fuel_types()
    employees = get_all_employees()
    customers = get_all_customers() if get_all_customers() else []

    with st.form("create_invoice_form"):
        col1, col2 = st.columns(2)

        with col1:
            invoice_no = st.text_input("رقم الفاتورة", max_chars=15, help="مثال: INV2024001")
            station_id = st.selectbox(
                "المحطة",
                [s[0] for s in stations] if stations else [""],
                format_func=lambda x: next((s[1] for s in stations if s[0] == x), x)
            )

            # Filter pumps by selected station
            station_pumps = [p for p in pumps if p[1] == station_id] if station_id else []
            pump_id = st.selectbox(
                "المضخة",
                [p[0] for p in station_pumps] if station_pumps else [""],
                format_func=lambda x: next((p[2] for p in station_pumps if p[0] == x), x) if station_pumps else "اختر المحطة أولاً"
            )

            # Filter tanks by selected station
            station_tanks = [t for t in tanks if t[1] == station_id] if station_id else []
            tank_id = st.selectbox(
                "الخزان",
                [t[0] for t in station_tanks] if station_tanks else [""],
                format_func=lambda x: next((t[3] for t in station_tanks if t[0] == x), x) if station_tanks else "اختر المحطة أولاً"
            )

        with col2:
            employee_id = st.selectbox(
                "الموظف",
                [""] + [e[0] for e in employees] if employees else [""],
                format_func=lambda x: next((e[2] for e in employees if e[0] == x), x) if x else "بدون موظف"
            )

            customer_code = st.selectbox(
                "العميل (اختياري)",
                [""] + [c[0] for c in customers] if customers else [""],
                format_func=lambda x: next((c[1] for c in customers if c[0] == x), x) if x else "عميل عابر"
            )

            fuel_type_id = st.selectbox(
                "نوع الوقود",
                [ft[0] for ft in fuel_types] if fuel_types else [""],
                format_func=lambda x: next((ft[1] for ft in fuel_types if ft[0] == x), x)
            )

            fuel_amount = st.number_input("كمية الوقود (لتر)", min_value=0.0, value=50.0, step=0.1)
            unit_price = st.number_input("السعر للتر", min_value=0.0, value=8.50, step=0.01)
            discount_percent = st.number_input("نسبة الخصم (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            payment_type = st.selectbox("طريقة الدفع", ["نقدي", "بطاقة ائتمانية", "شبكة", "شيك"])

        # Calculate totals
        discount_amount = (fuel_amount * unit_price * discount_percent) / 100
        total_amount = (fuel_amount * unit_price) - discount_amount

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("المبلغ الإجمالي", f"{fuel_amount * unit_price:.2f} ريال")
        with col2:
            st.metric("مبلغ الخصم", f"{discount_amount:.2f} ريال")
        with col3:
            st.metric("المبلغ النهائي", f"{total_amount:.2f} ريال")

        if st.form_submit_button("إنشاء الفاتورة", use_container_width=True):
            if invoice_no and station_id and pump_id and tank_id and fuel_type_id:
                if add_invoice(
                    invoice_no, station_id, pump_id, tank_id, employee_id if employee_id else None,
                    customer_code if customer_code else None, fuel_type_id, fuel_amount,
                    unit_price, discount_percent, payment_type
                ):
                    st.success("✅ تم إنشاء الفاتورة بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ خطأ في إنشاء الفاتورة")
            else:
                st.error("❌ يرجى ملء جميع الحقول المطلوبة")

def view_invoices_tab():
    """View all invoices"""
    st.subheader("📋 جميع الفواتير")

    invoices = get_all_invoices()

    if invoices:
        df = pd.DataFrame(invoices, columns=[
            'Invoice_No', 'Station_ID', 'Pump_ID', 'Tank_ID', 'Employee_ID',
            'Customer_Code', 'Invoice_Date', 'FuelType_ID', 'Fuel_Amount_Liters',
            'Unit_Price', 'Discount_Percent', 'Discount_Amount', 'Total_Amount',
            'Payment_Type', 'Payment_Status', 'Notes', 'Created_Date',
            'Station_Name', 'Pump_Name', 'Tank_Name', 'Employee_Name', 'C_Name', 'FuelType_Name'
        ])

        # Format numbers
        df['Unit_Price'] = df['Unit_Price'].apply(lambda x: f"{x:.2f} ريال")
        df['Total_Amount'] = df['Total_Amount'].apply(lambda x: f"{x:.2f} ريال")
        df['Fuel_Amount_Liters'] = df['Fuel_Amount_Liters'].apply(lambda x: f"{x:.1f} لتر")

        st.dataframe(df, use_container_width=True)

        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("إجمالي الفواتير", len(invoices))

        with col2:
            total_sales = sum(float(inv[12]) for inv in invoices)  # Total_Amount
            st.metric("إجمالي المبيعات", f"{total_sales:,.2f} ريال")

        with col3:
            avg_invoice = total_sales / len(invoices) if invoices else 0
            st.metric("متوسط الفاتورة", f"{avg_invoice:.2f} ريال")

        with col4:
            today_sales = sum(float(inv[12]) for inv in invoices if inv[6].date() == datetime.now().date())
            st.metric("مبيعات اليوم", f"{today_sales:.2f} ريال")

        # Filter options
        st.subheader("🔍 فلترة الفواتير")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Date filter
            date_filter = st.selectbox("الفترة الزمنية", [
                "الكل", "اليوم", "هذا الأسبوع", "هذا الشهر", "هذا العام"
            ])

        with col2:
            # Station filter
            stations = list(set(inv[17] for inv in invoices if inv[17]))
            station_filter = st.selectbox("المحطة", ["الكل"] + stations)

        with col3:
            # Payment type filter
            payment_types = list(set(inv[13] for inv in invoices if inv[13]))
            payment_filter = st.selectbox("طريقة الدفع", ["الكل"] + payment_types)

        # Apply filters
        filtered_invoices = invoices.copy()

        if date_filter != "الكل":
            today = datetime.now().date()
            if date_filter == "اليوم":
                filtered_invoices = [inv for inv in filtered_invoices if inv[6].date() == today]
            elif date_filter == "هذا الأسبوع":
                week_start = today - timedelta(days=today.weekday())
                filtered_invoices = [inv for inv in filtered_invoices if inv[6].date() >= week_start]
            elif date_filter == "هذا الشهر":
                filtered_invoices = [inv for inv in filtered_invoices if inv[6].month == today.month and inv[6].year == today.year]
            elif date_filter == "هذا العام":
                filtered_invoices = [inv for inv in filtered_invoices if inv[6].year == today.year]

        if station_filter != "الكل":
            filtered_invoices = [inv for inv in filtered_invoices if inv[17] == station_filter]

        if payment_filter != "الكل":
            filtered_invoices = [inv for inv in filtered_invoices if inv[13] == payment_filter]

        # Display filtered results
        if filtered_invoices:
            st.subheader(f"📋 النتائج المفلترة ({len(filtered_invoices)} فاتورة)")

            filtered_df = pd.DataFrame(filtered_invoices, columns=[
                'Invoice_No', 'Station_ID', 'Pump_ID', 'Tank_ID', 'Employee_ID',
                'Customer_Code', 'Invoice_Date', 'FuelType_ID', 'Fuel_Amount_Liters',
                'Unit_Price', 'Discount_Percent', 'Discount_Amount', 'Total_Amount',
                'Payment_Type', 'Payment_Status', 'Notes', 'Created_Date',
                'Station_Name', 'Pump_Name', 'Tank_Name', 'Employee_Name', 'C_Name', 'FuelType_Name'
            ])

            filtered_df['Unit_Price'] = filtered_df['Unit_Price'].apply(lambda x: f"{x:.2f} ريال")
            filtered_df['Total_Amount'] = filtered_df['Total_Amount'].apply(lambda x: f"{x:.2f} ريال")
            filtered_df['Fuel_Amount_Liters'] = filtered_df['Fuel_Amount_Liters'].apply(lambda x: f"{x:.1f} لتر")

            st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("ℹ️ لا توجد فواتير مسجلة")

def invoices_reports_tab():
    """Reports for invoices"""
    st.subheader("📊 تقارير الفواتير")

    invoices = get_all_invoices()

    if not invoices:
        st.info("ℹ️ لا توجد بيانات لعرض التقارير")
        return

    # Sales by station
    st.subheader("🏭 المبيعات حسب المحطة")

    station_sales = {}
    for inv in invoices:
        station_name = inv[17]  # Station_Name
        total_amount = float(inv[12])  # Total_Amount
        if station_name:
            station_sales[station_name] = station_sales.get(station_name, 0) + total_amount

    if station_sales:
        station_df = pd.DataFrame(list(station_sales.items()), columns=['المحطة', 'إجمالي المبيعات'])
        st.dataframe(station_df, use_container_width=True)

        # Chart
        st.bar_chart(station_df.set_index('المحطة'))

    # Sales by fuel type
    st.subheader("⛽ المبيعات حسب نوع الوقود")

    fuel_sales = {}
    for inv in invoices:
        fuel_name = inv[22]  # FuelType_Name
        total_amount = float(inv[12])  # Total_Amount
        if fuel_name:
            fuel_sales[fuel_name] = fuel_sales.get(fuel_name, 0) + total_amount

    if fuel_sales:
        fuel_df = pd.DataFrame(list(fuel_sales.items()), columns=['نوع الوقود', 'إجمالي المبيعات'])
        st.dataframe(fuel_df, use_container_width=True)

        # Chart
        st.bar_chart(fuel_df.set_index('نوع الوقود'))

    # Sales by payment type
    st.subheader("💳 المبيعات حسب طريقة الدفع")

    payment_sales = {}
    for inv in invoices:
        payment_type = inv[13]  # Payment_Type
        total_amount = float(inv[12])  # Total_Amount
        if payment_type:
            payment_sales[payment_type] = payment_sales.get(payment_type, 0) + total_amount

    if payment_sales:
        payment_df = pd.DataFrame(list(payment_sales.items()), columns=['طريقة الدفع', 'إجمالي المبيعات'])
        st.dataframe(payment_df, use_container_width=True)

        # Chart
        st.bar_chart(payment_df.set_index('طريقة الدفع'))

    # Daily sales trend (last 30 days)
    st.subheader("📈 اتجاه المبيعات اليومية")

    # Get last 30 days
    today = datetime.now().date()
    last_30_days = [(today - timedelta(days=i)) for i in range(29, -1, -1)]

    daily_sales = {}
    for day in last_30_days:
        daily_sales[day.strftime('%Y-%m-%d')] = 0

    for inv in invoices:
        inv_date = inv[6].date()
        if inv_date >= last_30_days[-1]:
            date_str = inv_date.strftime('%Y-%m-%d')
            daily_sales[date_str] = daily_sales.get(date_str, 0) + float(inv[12])

    if daily_sales:
        daily_df = pd.DataFrame(list(daily_sales.items()), columns=['التاريخ', 'المبيعات'])
        daily_df['التاريخ'] = pd.to_datetime(daily_df['التاريخ'])
        daily_df = daily_df.sort_values('التاريخ')

        st.line_chart(daily_df.set_index('التاريخ'))

if __name__ == "__main__":
    main()
