import streamlit as st
import pandas as pd
from core.database_enhanced import (
    get_all_stations, get_all_pumps, get_all_tanks, get_all_fuel_types,
    add_petrol_station, add_fuel_pump, add_fuel_tank,
    get_all_employees
)

def main():
    """Main management page for stations, pumps, and tanks"""

    st.title("🏭 إدارة المحطات والمضخات والخزانات")

    # Create tabs for different management sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏭 المحطات",
        "⛽ المضخات",
        "🗂️ الخزانات",
        "📊 التقارير"
    ])

    with tab1:
        stations_management()

    with tab2:
        pumps_management()

    with tab3:
        tanks_management()

    with tab4:
        stations_reports()

def stations_management():
    """Manage petrol stations"""
    st.subheader("🏭 إدارة المحطات")

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة محطة جديدة")

        with st.form("add_station_form"):
            station_id = st.text_input("رقم المحطة", max_chars=10)
            station_name = st.text_input("اسم المحطة", max_chars=100)
            company_name = st.text_input("اسم الشركة", max_chars=50)
            registration_no = st.text_input("رقم التسجيل", max_chars=20)
            opening_year = st.number_input("سنة الافتتاح", min_value=1900, max_value=2024, value=2024)
            state = st.text_input("المحافظة", max_chars=30)
            city = st.text_input("المدينة", max_chars=40)
            address = st.text_area("العنوان")
            phone = st.text_input("رقم الهاتف", max_chars=15)
            manager_id = st.text_input("رقم المدير", max_chars=10)

            if st.form_submit_button("إضافة المحطة", use_container_width=True):
                if station_id and station_name and city:
                    if add_petrol_station(
                        station_id, station_name, company_name, registration_no,
                        opening_year, state, city, address, phone, manager_id
                    ):
                        st.success("✅ تمت إضافة المحطة بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة المحطة")
                else:
                    st.error("❌ يرجى ملء جميع الحقول المطلوبة")

    with col2:
        st.markdown("### 📋 جميع المحطات")

        stations = get_all_stations()
        if stations:
            df = pd.DataFrame(stations, columns=[
                'Station_ID', 'Station_Name', 'Company_Name', 'Registration_No',
                'Opening_Year', 'State', 'City', 'Address', 'Phone', 'Manager_ID',
                'Total_Pumps', 'Total_Tanks', 'Is_Active', 'Created_Date'
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ لا توجد محطات مسجلة")

def pumps_management():
    """Manage fuel pumps"""
    st.subheader("⛽ إدارة المضخات")

    # Get data for dropdowns
    stations = get_all_stations()
    fuel_types = get_all_fuel_types()
    tanks = get_all_tanks()
    employees = get_all_employees()

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة مضخة جديدة")

        with st.form("add_pump_form"):
            pump_id = st.text_input("رقم المضخة", max_chars=10)
            station_id = st.selectbox(
                "المحطة",
                [s[0] for s in stations] if stations else [""],
                format_func=lambda x: next((s[1] for s in stations if s[0] == x), x)
            )
            pump_name = st.text_input("اسم المضخة", max_chars=50)
            pump_number = st.number_input("رقم المضخة", min_value=1, max_value=99, value=1)
            location = st.text_input("الموقع", max_chars=50)

            fuel_type_id = st.selectbox(
                "نوع الوقود",
                [ft[0] for ft in fuel_types] if fuel_types else [""],
                format_func=lambda x: next((ft[1] for ft in fuel_types if ft[0] == x), x)
            )

            tank_id = st.selectbox(
                "الخزان المرتبط",
                [""] + [t[0] for t in tanks] if tanks else [""],
                format_func=lambda x: next((t[1] for t in tanks if t[0] == x), x) if x else "بدون خزان"
            )

            employee_id = st.selectbox(
                "الموظف المسؤول",
                [""] + [e[0] for e in employees] if employees else [""],
                format_func=lambda x: next((e[2] for e in employees if e[0] == x), x) if x else "بدون موظف"
            )

            max_flow_rate = st.number_input("معدل التدفق الأقصى (لتر/دقيقة)", min_value=0.0, value=50.0)

            if st.form_submit_button("إضافة المضخة", use_container_width=True):
                if pump_id and station_id and pump_name and fuel_type_id:
                    if add_fuel_pump(
                        pump_id, station_id, pump_name, pump_number, location,
                        fuel_type_id, tank_id if tank_id else None, employee_id if employee_id else None
                    ):
                        st.success("✅ تمت إضافة المضخة بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة المضخة")
                else:
                    st.error("❌ يرجى ملء جميع الحقول المطلوبة")

    with col2:
        st.markdown("### 📋 جميع المضخات")

        pumps = get_all_pumps()
        if pumps:
            df = pd.DataFrame(pumps, columns=[
                'Pump_ID', 'Station_ID', 'Pump_Name', 'Pump_Number', 'Location',
                'FuelType_ID', 'Tank_ID', 'Employee_ID', 'Max_Flow_Rate',
                'Is_Active', 'Last_Service', 'Next_Service', 'Total_Liters_Dispensed', 'Created_Date',
                'Station_Name', 'FuelType_Name', 'Tank_Name', 'Employee_Name'
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ لا توجد مضخات مسجلة")

def tanks_management():
    """Manage fuel tanks"""
    st.subheader("🗂️ إدارة الخزانات")

    # Get data for dropdowns
    stations = get_all_stations()
    fuel_types = get_all_fuel_types()

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة خزان جديد")

        with st.form("add_tank_form"):
            tank_id = st.text_input("رقم الخزان", max_chars=10)
            station_id = st.selectbox(
                "المحطة",
                [s[0] for s in stations] if stations else [""],
                format_func=lambda x: next((s[1] for s in stations if s[0] == x), x)
            )
            fuel_type_id = st.selectbox(
                "نوع الوقود",
                [ft[0] for ft in fuel_types] if fuel_types else [""],
                format_func=lambda x: next((ft[1] for ft in fuel_types if ft[0] == x), x)
            )
            tank_name = st.text_input("اسم الخزان", max_chars=50)
            capacity_liters = st.number_input("السعة (لتر)", min_value=0.0, value=50000.0)
            max_pressure = st.number_input("الضغط الأقصى", min_value=0.0, value=5.0)
            min_pressure = st.number_input("الضغط الأدنى", min_value=0.0, value=1.0)
            location = st.text_input("الموقع", max_chars=50)

            if st.form_submit_button("إضافة الخزان", use_container_width=True):
                if tank_id and station_id and fuel_type_id and tank_name:
                    if add_fuel_tank(
                        tank_id, station_id, fuel_type_id, tank_name,
                        capacity_liters, max_pressure, min_pressure, location
                    ):
                        st.success("✅ تمت إضافة الخزان بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة الخزان")
                else:
                    st.error("❌ يرجى ملء جميع الحقول المطلوبة")

    with col2:
        st.markdown("### 📋 جميع الخزانات")

        tanks = get_all_tanks()
        if tanks:
            df = pd.DataFrame(tanks, columns=[
                'Tank_ID', 'Station_ID', 'FuelType_ID', 'Tank_Name', 'Capacity_Liters',
                'Current_Amount_Liters', 'Max_Pressure', 'Min_Pressure', 'Location',
                'Is_Active', 'Last_Maintenance', 'Next_Maintenance', 'Created_Date',
                'Station_Name', 'FuelType_Name'
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ لا توجد خزانات مسجلة")

def stations_reports():
    """Reports for stations, pumps, and tanks"""
    st.subheader("📊 تقارير المحطات والمضخات والخزانات")

    # Get data
    stations = get_all_stations()
    pumps = get_all_pumps()
    tanks = get_all_tanks()

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("إجمالي المحطات", len(stations))

    with col2:
        st.metric("إجمالي المضخات", len(pumps))

    with col3:
        st.metric("إجمالي الخزانات", len(tanks))

    with col4:
        active_pumps = len([p for p in pumps if p[9]])  # Is_Active column
        st.metric("المضخات النشطة", active_pumps)

    # Detailed reports
    st.markdown("---")

    # Stations by city
    if stations:
        st.subheader("🏙️ المحطات حسب المدينة")

        cities = {}
        for station in stations:
            city = station[6]  # City column
            if city:
                cities[city] = cities.get(city, 0) + 1

        if cities:
            city_df = pd.DataFrame(list(cities.items()), columns=['المدينة', 'عدد المحطات'])
            st.bar_chart(city_df.set_index('المدينة'))

    # Pumps by fuel type
    if pumps:
        st.subheader("⛽ المضخات حسب نوع الوقود")

        fuel_types = {}
        for pump in pumps:
            fuel_type = pump[15]  # FuelType_Name column
            if fuel_type:
                fuel_types[fuel_type] = fuel_types.get(fuel_type, 0) + 1

        if fuel_types:
            fuel_df = pd.DataFrame(list(fuel_types.items()), columns=['نوع الوقود', 'عدد المضخات'])
            st.bar_chart(fuel_df.set_index('نوع الوقود'))

    # Tank capacity utilization
    if tanks:
        st.subheader("🗂️ استخدام سعة الخزانات")

        tank_data = []
        for tank in tanks:
            tank_id = tank[0]
            tank_name = tank[3]
            capacity = float(tank[4])
            current = float(tank[5])
            utilization = (current / capacity * 100) if capacity > 0 else 0

            tank_data.append({
                'الخزان': tank_name,
                'السعة': capacity,
                'الكمية الحالية': current,
                'نسبة الاستخدام %': round(utilization, 1)
            })

        if tank_data:
            tank_df = pd.DataFrame(tank_data)
            st.dataframe(tank_df, use_container_width=True)

            # Color coding for utilization
            st.markdown("""
            <style>
            .low-util { color: green; }
            .med-util { color: orange; }
            .high-util { color: red; }
            </style>
            """, unsafe_allow_html=True)

            for _, row in tank_df.iterrows():
                if row['نسبة الاستخدام %'] < 30:
                    st.markdown(f"🟢 **{row['الخزان']}**: {row['نسبة الاستخدام %']}% (منخفض)")
                elif row['نسبة الاستخدام %'] < 70:
                    st.markdown(f"🟡 **{row['الخزان']}**: {row['نسبة الاستخدام %']}% (متوسط)")
                else:
                    st.markdown(f"🔴 **{row['الخزان']}**: {row['نسبة الاستخدام %']}% (مرتفع)")

if __name__ == "__main__":
    main()
