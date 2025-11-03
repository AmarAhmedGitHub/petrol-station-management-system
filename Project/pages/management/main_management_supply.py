import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from core.database_enhanced import (
    get_all_supplies, add_fuel_supply, get_all_stations, get_all_tanks, get_all_fuel_types
)

def main():
    """Main management page for fuel supply"""

    st.title("🚛 إدارة توريد الوقود")

    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs([
        "➕ إضافة توريد",
        "📋 جميع عمليات التوريد",
        "📊 تقارير التوريد"
    ])

    with tab1:
        add_supply_tab()

    with tab2:
        view_supplies_tab()

    with tab3:
        supplies_reports_tab()

def add_supply_tab():
    """Add new fuel supply"""
    st.subheader("➕ إضافة توريد وقود جديد")

    # Get data for dropdowns
    stations = get_all_stations()
    tanks = get_all_tanks()
    fuel_types = get_all_fuel_types()

    with st.form("add_supply_form"):
        col1, col2 = st.columns(2)

        with col1:
            supply_invoice_no = st.text_input("رقم فاتورة التوريد", max_chars=20, help="مثال: SUP2024001")
            station_id = st.selectbox(
                "المحطة",
                [s[0] for s in stations] if stations else [""],
                format_func=lambda x: next((s[1] for s in stations if s[0] == x), x)
            )

            # Filter tanks by selected station
            station_tanks = [t for t in tanks if t[1] == station_id] if station_id else []
            tank_id = st.selectbox(
                "الخزان",
                [t[0] for t in station_tanks] if station_tanks else [""],
                format_func=lambda x: next((t[3] for t in station_tanks if t[0] == x), x) if station_tanks else "اختر المحطة أولاً"
            )

            fuel_type_id = st.selectbox(
                "نوع الوقود",
                [ft[0] for ft in fuel_types] if fuel_types else [""],
                format_func=lambda x: next((ft[1] for ft in fuel_types if ft[0] == x), x)
            )

            supply_date = st.date_input("تاريخ التوريد", value=datetime.now().date())
            supplier_name = st.text_input("اسم المورد", max_chars=100)

        with col2:
            quantity_liters = st.number_input("الكمية (لتر)", min_value=0.0, value=20000.0, step=100.0)
            unit_price = st.number_input("السعر للتر", min_value=0.0, value=8.50, step=0.01)
            supply_type = st.selectbox("نوع التوريد", [
                "توصيل", "شحن", "نقل داخلي", "طوارئ"
            ])
            notes = st.text_area("ملاحظات", height=80)

        # Calculate totals
        total_amount = quantity_liters * unit_price

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي الكمية", f"{quantity_liters:,.0f} لتر")
        with col2:
            st.metric("السعر للتر", f"{unit_price:.2f} ريال")
        with col3:
            st.metric("المبلغ الإجمالي", f"{total_amount:,.2f} ريال")

        if st.form_submit_button("إضافة التوريد", use_container_width=True):
            if supply_invoice_no and station_id and tank_id and fuel_type_id:
                if add_fuel_supply(
                    station_id, tank_id, fuel_type_id, supply_invoice_no, supply_date,
                    supplier_name, quantity_liters, unit_price, supply_type, notes
                ):
                    st.success("✅ تمت إضافة عملية التوريد بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ خطأ في إضافة عملية التوريد")
            else:
                st.error("❌ يرجى ملء جميع الحقول المطلوبة")

def view_supplies_tab():
    """View all fuel supplies"""
    st.subheader("📋 جميع عمليات التوريد")

    supplies = get_all_supplies()

    if supplies:
        df = pd.DataFrame(supplies, columns=[
            'Supply_ID', 'Station_ID', 'Tank_ID', 'FuelType_ID', 'Supply_Invoice_No',
            'Supply_Date', 'Supplier_Name', 'Quantity_Liters', 'Unit_Price',
            'Total_Amount', 'Previous_Amount', 'New_Amount', 'Supply_Type',
            'Notes', 'Created_Date', 'Station_Name', 'Tank_Name', 'FuelType_Name'
        ])

        # Format numbers
        df['Quantity_Liters'] = df['Quantity_Liters'].apply(lambda x: f"{x:,.0f} لتر")
        df['Unit_Price'] = df['Unit_Price'].apply(lambda x: f"{x:.2f} ريال")
        df['Total_Amount'] = df['Total_Amount'].apply(lambda x: f"{x:,.2f} ريال")
        df['Previous_Amount'] = df['Previous_Amount'].apply(lambda x: f"{x:,.0f} لتر" if x else "0 لتر")
        df['New_Amount'] = df['New_Amount'].apply(lambda x: f"{x:,.0f} لتر" if x else "0 لتر")

        st.dataframe(df, use_container_width=True)

        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("إجمالي عمليات التوريد", len(supplies))

        with col2:
            total_quantity = sum(float(s[7]) for s in supplies)  # Quantity_Liters
            st.metric("إجمالي الكمية", f"{total_quantity:,.0f} لتر")

        with col3:
            total_amount = sum(float(s[9]) for s in supplies)  # Total_Amount
            st.metric("إجمالي المبلغ", f"{total_amount:,.2f} ريال")

        with col4:
            avg_quantity = total_quantity / len(supplies) if supplies else 0
            st.metric("متوسط الكمية", f"{avg_quantity:.0f} لتر")

        # Filter options
        st.subheader("🔍 فلترة عمليات التوريد")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Date filter
            date_filter = st.selectbox("الفترة الزمنية", [
                "الكل", "اليوم", "هذا الأسبوع", "هذا الشهر", "هذا العام"
            ])

        with col2:
            # Station filter
            stations = list(set(s[15] for s in supplies if s[15]))  # Station_Name
            station_filter = st.selectbox("المحطة", ["الكل"] + stations)

        with col3:
            # Supply type filter
            supply_types = list(set(s[12] for s in supplies if s[12]))  # Supply_Type
            supply_type_filter = st.selectbox("نوع التوريد", ["الكل"] + supply_types)

        # Apply filters
        filtered_supplies = supplies.copy()

        if date_filter != "الكل":
            today = datetime.now().date()
            if date_filter == "اليوم":
                filtered_supplies = [s for s in filtered_supplies if s[5] == today]
            elif date_filter == "هذا الأسبوع":
                week_start = today - timedelta(days=today.weekday())
                filtered_supplies = [s for s in filtered_supplies if s[5] >= week_start]
            elif date_filter == "هذا الشهر":
                filtered_supplies = [s for s in filtered_supplies if s[5].month == today.month and s[5].year == today.year]
            elif date_filter == "هذا العام":
                filtered_supplies = [s for s in filtered_supplies if s[5].year == today.year]

        if station_filter != "الكل":
            filtered_supplies = [s for s in filtered_supplies if s[15] == station_filter]

        if supply_type_filter != "الكل":
            filtered_supplies = [s for s in filtered_supplies if s[12] == supply_type_filter]

        # Display filtered results
        if filtered_supplies:
            st.subheader(f"📋 النتائج المفلترة ({len(filtered_supplies)} عملية)")

            filtered_df = pd.DataFrame(filtered_supplies, columns=[
                'Supply_ID', 'Station_ID', 'Tank_ID', 'FuelType_ID', 'Supply_Invoice_No',
                'Supply_Date', 'Supplier_Name', 'Quantity_Liters', 'Unit_Price',
                'Total_Amount', 'Previous_Amount', 'New_Amount', 'Supply_Type',
                'Notes', 'Created_Date', 'Station_Name', 'Tank_Name', 'FuelType_Name'
            ])

            filtered_df['Quantity_Liters'] = filtered_df['Quantity_Liters'].apply(lambda x: f"{x:,.0f} لتر")
            filtered_df['Unit_Price'] = filtered_df['Unit_Price'].apply(lambda x: f"{x:.2f} ريال")
            filtered_df['Total_Amount'] = filtered_df['Total_Amount'].apply(lambda x: f"{x:,.2f} ريال")
            filtered_df['Previous_Amount'] = filtered_df['Previous_Amount'].apply(lambda x: f"{x:,.0f} لتر" if x else "0 لتر")
            filtered_df['New_Amount'] = filtered_df['New_Amount'].apply(lambda x: f"{x:,.0f} لتر" if x else "0 لتر")

            st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("ℹ️ لا توجد عمليات توريد مسجلة")

def supplies_reports_tab():
    """Reports for fuel supplies"""
    st.subheader("📊 تقارير توريد الوقود")

    supplies = get_all_supplies()

    if not supplies:
        st.info("ℹ️ لا توجد بيانات لعرض التقارير")
        return

    # Supply by station
    st.subheader("🏭 التوريد حسب المحطة")

    station_supply = {}
    for supply in supplies:
        station_name = supply[15]  # Station_Name
        total_amount = float(supply[9])  # Total_Amount
        if station_name:
            station_supply[station_name] = station_supply.get(station_name, 0) + total_amount

    if station_supply:
        station_df = pd.DataFrame(list(station_supply.items()), columns=['المحطة', 'إجمالي التوريد'])
        st.dataframe(station_df, use_container_width=True)

        # Chart
        st.bar_chart(station_df.set_index('المحطة'))

    # Supply by fuel type
    st.subheader("⛽ التوريد حسب نوع الوقود")

    fuel_supply = {}
    for supply in supplies:
        fuel_name = supply[17]  # FuelType_Name
        quantity = float(supply[7])  # Quantity_Liters
        if fuel_name:
            fuel_supply[fuel_name] = fuel_supply.get(fuel_name, 0) + quantity

    if fuel_supply:
        fuel_df = pd.DataFrame(list(fuel_supply.items()), columns=['نوع الوقود', 'إجمالي الكمية'])
        st.dataframe(fuel_df, use_container_width=True)

        # Chart
        st.bar_chart(fuel_df.set_index('نوع الوقود'))

    # Supply by supplier
    st.subheader("🏢 التوريد حسب المورد")

    supplier_supply = {}
    for supply in supplies:
        supplier_name = supply[6]  # Supplier_Name
        total_amount = float(supply[9])  # Total_Amount
        if supplier_name:
            supplier_supply[supplier_name] = supplier_supply.get(supplier_name, 0) + total_amount

    if supplier_supply:
        supplier_df = pd.DataFrame(list(supplier_supply.items()), columns=['المورد', 'إجمالي المبلغ'])
        st.dataframe(supplier_df, use_container_width=True)

        # Chart
        st.bar_chart(supplier_df.set_index('المورد'))

    # Monthly supply trend
    st.subheader("📈 اتجاه التوريد الشهري")

    # Group by month
    monthly_supply = {}
    for supply in supplies:
        supply_date = supply[5]  # Supply_Date
        if isinstance(supply_date, str):
            try:
                supply_date = pd.to_datetime(supply_date).date()
            except:
                continue

        month_key = supply_date.strftime('%Y-%m')
        total_amount = float(supply[9])  # Total_Amount
        monthly_supply[month_key] = monthly_supply.get(month_key, 0) + total_amount

    if monthly_supply:
        monthly_df = pd.DataFrame(list(monthly_supply.items()), columns=['الشهر', 'إجمالي المبلغ'])
        monthly_df['الشهر'] = pd.to_datetime(monthly_df['الشهر'])
        monthly_df = monthly_df.sort_values('الشهر')

        st.line_chart(monthly_df.set_index('الشهر'))

    # Supply efficiency analysis
    st.subheader("⚡ تحليل كفاءة التوريد")

    if supplies:
        # Calculate average supply size
        quantities = [float(s[7]) for s in supplies]  # Quantity_Liters
        avg_supply_size = sum(quantities) / len(quantities)

        # Calculate supply frequency (days between supplies)
        supply_dates = sorted([s[5] for s in supplies if s[5]])
        supply_intervals = []
        for i in range(1, len(supply_dates)):
            if isinstance(supply_dates[i], str):
                try:
                    date1 = pd.to_datetime(supply_dates[i-1]).date()
                    date2 = pd.to_datetime(supply_dates[i]).date()
                    interval = (date2 - date1).days
                    supply_intervals.append(interval)
                except:
                    continue

        avg_interval = sum(supply_intervals) / len(supply_intervals) if supply_intervals else 0

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("متوسط حجم التوريد", f"{avg_supply_size:,.0f} لتر")

        with col2:
            st.metric("متوسط الفترة بين التوريد", f"{avg_interval:.1f} يوم")

        with col3:
            monthly_avg = len(supplies) / max(1, len(set(s[5].strftime('%Y-%m') for s in supplies if s[5])))
            st.metric("متوسط التوريد شهرياً", f"{monthly_avg:.1f} عملية")

if __name__ == "__main__":
    main()
