import streamlit as st
import pandas as pd
from core.database_enhanced import (
    # Dispensers
    add_dispenser, get_all_dispensers,
    # Nozzles
    add_nozzle, get_all_nozzles,
    # Flowmeters
    add_flowmeter, get_all_flowmeters,
    # Price Signs
    add_price_sign, get_all_price_signs,
    # Payment Terminals
    add_payment_terminal, get_all_payment_terminals,
    # AVI Vehicles
    add_avi_vehicle, get_all_avi_vehicles,
    # RFID Readers
    add_rfid_reader, get_all_rfid_readers,
    # Forecourt Controllers
    add_forecourt_controller, get_all_forecourt_controllers,
    # System Logs
    add_system_log, get_all_system_logs,
    # Supporting data
    get_all_stations, get_all_fuel_types, get_all_customers
)

def main():
    """Main hardware management page for dispensers, nozzles, flowmeters, and other hardware"""

    st.title("🔧 إدارة الأجهزة والمعدات")

    # Create tabs for different hardware categories
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "⛽ الموزعات",
        "🔧 الفوهات",
        "📊 عدادات التدفق",
        "💰 لوحات الأسعار",
        "💳 الأجهزة الطرفية",
        "🚗 مركبات AVI",
        "📡 قارئات RFID",
        "🎛️ وحدات التحكم",
        "📋 سجلات النظام"
    ])

    with tab1:
        dispensers_management()

    with tab2:
        nozzles_management()

    with tab3:
        flowmeters_management()

    with tab4:
        price_signs_management()

    with tab5:
        payment_terminals_management()

    with tab6:
        avi_vehicles_management()

    with tab7:
        rfid_readers_management()

    with tab8:
        forecourt_controllers_management()

    with tab9:
        system_logs_management()

def dispensers_management():
    """Manage fuel dispensers"""
    st.subheader("⛽ إدارة الموزعات")

    # Get data for dropdowns
    stations = get_all_stations()

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة موزع جديد")

        with st.form("add_dispenser_form"):
            dispenser_id = st.text_input("رقم الموزع", max_chars=10)
            station_id = st.selectbox(
                "المحطة",
                [s[0] for s in stations] if stations else [""],
                format_func=lambda x: next((s[1] for s in stations if s[0] == x), x)
            )
            serial_number = st.text_input("الرقم التسلسلي", max_chars=50)
            status = st.selectbox("الحالة", ['active', 'inactive', 'maintenance'], index=0)

            if st.form_submit_button("إضافة الموزع", use_container_width=True):
                if dispenser_id and station_id and serial_number:
                    if add_dispenser(dispenser_id, station_id, serial_number, status):
                        st.success("✅ تمت إضافة الموزع بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة الموزع")
                else:
                    st.error("❌ يرجى ملء جميع الحقول المطلوبة")

    with col2:
        st.markdown("### 📋 جميع الموزعات")

        dispensers = get_all_dispensers()
        if dispensers:
            df = pd.DataFrame(dispensers, columns=[
                'Dispenser_ID', 'Station_ID', 'Serial_Number', 'Status',
                'Last_Communication', 'Created_Date', 'Station_Name'
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ لا توجد موزعات مسجلة")

def nozzles_management():
    """Manage fuel nozzles"""
    st.subheader("🔧 إدارة الفوهات")

    # Get data for dropdowns
    dispensers = get_all_dispensers()
    fuel_types = get_all_fuel_types()

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة فوهة جديدة")

        with st.form("add_nozzle_form"):
            nozzle_id = st.text_input("رقم الفوهة", max_chars=10)
            dispenser_id = st.selectbox(
                "الموزع",
                [d[0] for d in dispensers] if dispensers else [""],
                format_func=lambda x: next((f"{d[0]} ({d[2]})" for d in dispensers if d[0] == x), x)
            )
            fuel_type_id = st.selectbox(
                "نوع الوقود",
                [ft[0] for ft in fuel_types] if fuel_types else [""],
                format_func=lambda x: next((ft[1] for ft in fuel_types if ft[0] == x), x)
            )
            meter_reading_start = st.number_input("قراءة العداد البداية", min_value=0.0, value=0.0, step=0.001)
            meter_reading_current = st.number_input("قراءة العداد الحالية", min_value=0.0, value=0.0, step=0.001)

            if st.form_submit_button("إضافة الفوهة", use_container_width=True):
                if nozzle_id and dispenser_id and fuel_type_id:
                    if add_nozzle(nozzle_id, dispenser_id, fuel_type_id, meter_reading_start, meter_reading_current):
                        st.success("✅ تمت إضافة الفوهة بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة الفوهة")
                else:
                    st.error("❌ يرجى ملء جميع الحقول المطلوبة")

    with col2:
        st.markdown("### 📋 جميع الفوهات")

        nozzles = get_all_nozzles()
        if nozzles:
            df = pd.DataFrame(nozzles, columns=[
                'Nozzle_ID', 'Dispenser_ID', 'FuelType_ID', 'Meter_Reading_Start',
                'Meter_Reading_Current', 'Created_Date', 'Dispenser_Serial', 'FuelType_Name'
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ لا توجد فوهات مسجلة")

def flowmeters_management():
    """Manage flowmeters"""
    st.subheader("📊 إدارة عدادات التدفق")

    # Get data for dropdowns
    stations = get_all_stations()
    fuel_types = get_all_fuel_types()

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة عداد تدفق جديد")

        with st.form("add_flowmeter_form"):
            flowmeter_id = st.text_input("رقم عداد التدفق", max_chars=10)
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
            serial_number = st.text_input("الرقم التسلسلي", max_chars=50)
            total_flow_liters = st.number_input("إجمالي التدفق (لتر)", min_value=0.0, value=0.0, step=0.001)

            if st.form_submit_button("إضافة عداد التدفق", use_container_width=True):
                if flowmeter_id and station_id and fuel_type_id and serial_number:
                    if add_flowmeter(flowmeter_id, station_id, fuel_type_id, serial_number, total_flow_liters):
                        st.success("✅ تمت إضافة عداد التدفق بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة عداد التدفق")
                else:
                    st.error("❌ يرجى ملء جميع الحقول المطلوبة")

    with col2:
        st.markdown("### 📋 جميع عدادات التدفق")

        flowmeters = get_all_flowmeters()
        if flowmeters:
            df = pd.DataFrame(flowmeters, columns=[
                'Flowmeter_ID', 'Station_ID', 'FuelType_ID', 'Serial_Number',
                'Total_Flow_Liters', 'Last_Reading_Timestamp', 'Created_Date',
                'Station_Name', 'FuelType_Name'
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ لا توجد عدادات تدفق مسجلة")

def price_signs_management():
    """Manage price signs"""
    st.subheader("💰 إدارة لوحات الأسعار")

    # Get data for dropdowns
    stations = get_all_stations()
    fuel_types = get_all_fuel_types()

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة لوحة سعر جديدة")

        with st.form("add_price_sign_form"):
            price_sign_id = st.text_input("رقم لوحة السعر", max_chars=10)
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
            price = st.number_input("السعر", min_value=0.0, value=8.50, step=0.001)

            if st.form_submit_button("إضافة لوحة السعر", use_container_width=True):
                if price_sign_id and station_id and fuel_type_id:
                    if add_price_sign(price_sign_id, station_id, fuel_type_id, price):
                        st.success("✅ تمت إضافة لوحة السعر بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة لوحة السعر")
                else:
                    st.error("❌ يرجى ملء جميع الحقول المطلوبة")

    with col2:
        st.markdown("### 📋 جميع لوحات الأسعار")

        price_signs = get_all_price_signs()
        if price_signs:
            df = pd.DataFrame(price_signs, columns=[
                'PriceSign_ID', 'Station_ID', 'FuelType_ID', 'Price',
                'Last_Updated', 'Created_Date', 'Station_Name', 'FuelType_Name'
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ لا توجد لوحات أسعار مسجلة")

def payment_terminals_management():
    """Manage payment terminals"""
    st.subheader("💳 إدارة الأجهزة الطرفية")

    # Get data for dropdowns
    stations = get_all_stations()

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة جهاز طرفي جديد")

        with st.form("add_payment_terminal_form"):
            terminal_id = st.text_input("رقم الجهاز الطرفي", max_chars=10)
            station_id = st.selectbox(
                "المحطة",
                [s[0] for s in stations] if stations else [""],
                format_func=lambda x: next((s[1] for s in stations if s[0] == x), x)
            )
            terminal_type = st.selectbox("نوع الجهاز", ['POS', 'Outdoor', 'Mobile'], index=0)
            serial_number = st.text_input("الرقم التسلسلي", max_chars=50)
            status = st.selectbox("الحالة", ['active', 'inactive', 'maintenance'], index=0)

            if st.form_submit_button("إضافة الجهاز الطرفي", use_container_width=True):
                if terminal_id and station_id and terminal_type and serial_number:
                    if add_payment_terminal(terminal_id, station_id, terminal_type, serial_number, status):
                        st.success("✅ تمت إضافة الجهاز الطرفي بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة الجهاز الطرفي")
                else:
                    st.error("❌ يرجى ملء جميع الحقول المطلوبة")

    with col2:
        st.markdown("### 📋 جميع الأجهزة الطرفية")

        terminals = get_all_payment_terminals()
        if terminals:
            df = pd.DataFrame(terminals, columns=[
                'Terminal_ID', 'Station_ID', 'Type', 'Serial_Number', 'Status',
                'Last_Communication', 'Created_Date', 'Station_Name'
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ لا توجد أجهزة طرفية مسجلة")

def avi_vehicles_management():
    """Manage AVI vehicles"""
    st.subheader("🚗 إدارة مركبات AVI")

    # Get data for dropdowns
    customers = get_all_customers()
    fuel_types = get_all_fuel_types()

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة مركبة AVI جديدة")

        with st.form("add_avi_vehicle_form"):
            vehicle_id = st.text_input("رقم المركبة", max_chars=10)
            rfid_tag = st.text_input("علامة RFID", max_chars=50)
            license_plate = st.text_input("رقم اللوحة", max_chars=20)
            customer_id = st.selectbox(
                "العميل",
                [""] + [c[0] for c in customers] if customers else [""],
                format_func=lambda x: next((c[1] for c in customers if c[0] == x), x) if x else "بدون عميل"
            )
            fuel_type_id = st.selectbox(
                "نوع الوقود المفضل",
                [""] + [ft[0] for ft in fuel_types] if fuel_types else [""],
                format_func=lambda x: next((ft[1] for ft in fuel_types if ft[0] == x), x) if x else "غير محدد"
            )

            if st.form_submit_button("إضافة مركبة AVI", use_container_width=True):
                if vehicle_id and rfid_tag:
                    if add_avi_vehicle(vehicle_id, rfid_tag, license_plate, customer_id if customer_id else None, fuel_type_id if fuel_type_id else None):
                        st.success("✅ تمت إضافة مركبة AVI بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة مركبة AVI")
                else:
                    st.error("❌ يرجى ملء الحقول المطلوبة (رقم المركبة وعلامة RFID)")

    with col2:
        st.markdown("### 📋 جميع مركبات AVI")

        avi_vehicles = get_all_avi_vehicles()
        if avi_vehicles:
            df = pd.DataFrame(avi_vehicles, columns=[
                'Vehicle_ID', 'RFID_Tag', 'License_Plate', 'Customer_ID',
                'FuelType_ID', 'Last_Seen', 'Created_Date', 'Customer_Name', 'FuelType_Name'
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ لا توجد مركبات AVI مسجلة")

def rfid_readers_management():
    """Manage RFID readers"""
    st.subheader("📡 إدارة قارئات RFID")

    # Get data for dropdowns
    stations = get_all_stations()

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة قارئ RFID جديد")

        with st.form("add_rfid_reader_form"):
            reader_id = st.text_input("رقم القارئ", max_chars=10)
            station_id = st.selectbox(
                "المحطة",
                [s[0] for s in stations] if stations else [""],
                format_func=lambda x: next((s[1] for s in stations if s[0] == x), x)
            )
            serial_number = st.text_input("الرقم التسلسلي", max_chars=50)
            location = st.text_input("الموقع", max_chars=100)
            status = st.selectbox("الحالة", ['active', 'inactive', 'maintenance'], index=0)

            if st.form_submit_button("إضافة قارئ RFID", use_container_width=True):
                if reader_id and station_id and serial_number:
                    if add_rfid_reader(reader_id, station_id, serial_number, location, status):
                        st.success("✅ تمت إضافة قارئ RFID بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة قارئ RFID")
                else:
                    st.error("❌ يرجى ملء جميع الحقول المطلوبة")

    with col2:
        st.markdown("### 📋 جميع قارئات RFID")

        rfid_readers = get_all_rfid_readers()
        if rfid_readers:
            df = pd.DataFrame(rfid_readers, columns=[
                'Reader_ID', 'Station_ID', 'Serial_Number', 'Location', 'Status',
                'Last_Communication', 'Created_Date', 'Station_Name'
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ لا توجد قارئات RFID مسجلة")

def forecourt_controllers_management():
    """Manage forecourt controllers"""
    st.subheader("🎛️ إدارة وحدات التحكم")

    # Get data for dropdowns
    stations = get_all_stations()

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة وحدة تحكم جديدة")

        with st.form("add_forecourt_controller_form"):
            controller_id = st.text_input("رقم وحدة التحكم", max_chars=10)
            station_id = st.selectbox(
                "المحطة",
                [s[0] for s in stations] if stations else [""],
                format_func=lambda x: next((s[1] for s in stations if s[0] == x), x)
            )
            serial_number = st.text_input("الرقم التسلسلي", max_chars=50)
            ip_address = st.text_input("عنوان IP", max_chars=15)
            firmware_version = st.text_input("إصدار البرنامج الثابت", max_chars=50)
            status = st.selectbox("الحالة", ['online', 'offline', 'error'], index=0)

            if st.form_submit_button("إضافة وحدة التحكم", use_container_width=True):
                if controller_id and station_id and serial_number:
                    if add_forecourt_controller(controller_id, station_id, serial_number, ip_address, firmware_version, status):
                        st.success("✅ تمت إضافة وحدة التحكم بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة وحدة التحكم")
                else:
                    st.error("❌ يرجى ملء جميع الحقول المطلوبة")

    with col2:
        st.markdown("### 📋 جميع وحدات التحكم")

        controllers = get_all_forecourt_controllers()
        if controllers:
            df = pd.DataFrame(controllers, columns=[
                'Controller_ID', 'Station_ID', 'Serial_Number', 'IP_Address',
                'Firmware_Version', 'Status', 'Last_Heartbeat', 'Created_Date', 'Station_Name'
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ لا توجد وحدات تحكم مسجلة")

def system_logs_management():
    """View and manage system logs"""
    st.subheader("📋 سجلات النظام")

    # Get data for dropdowns
    stations = get_all_stations()

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة سجل نظام جديد")

        with st.form("add_system_log_form"):
            station_id = st.selectbox(
                "المحطة",
                [""] + [s[0] for s in stations] if stations else [""],
                format_func=lambda x: next((s[1] for s in stations if s[0] == x), x) if x else "عام"
            )
            event_type = st.text_input("نوع الحدث", max_chars=100)
            description = st.text_area("الوصف")
            severity = st.selectbox("مستوى الخطورة", ['info', 'warning', 'error', 'critical'], index=0)

            if st.form_submit_button("إضافة السجل", use_container_width=True):
                if event_type and description:
                    if add_system_log(station_id if station_id else None, event_type, description, severity):
                        st.success("✅ تمت إضافة السجل بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة السجل")
                else:
                    st.error("❌ يرجى ملء الحقول المطلوبة (نوع الحدث والوصف)")

    with col2:
        st.markdown("### 📋 آخر 100 سجل")

        # Filters
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            severity_filter = st.selectbox("تصفية حسب الخطورة", ['الكل', 'info', 'warning', 'error', 'critical'], index=0)
        with col_filter2:
            station_filter = st.selectbox(
                "تصفية حسب المحطة",
                ['الكل'] + [s[1] for s in stations] if stations else ['الكل'],
                index=0
            )

        logs = get_all_system_logs(100)
        if logs:
            # Apply filters
            if severity_filter != 'الكل':
                logs = [log for log in logs if log[3] == severity_filter]  # Severity column

            if station_filter != 'الكل':
                logs = [log for log in logs if log[9] == station_filter]  # Station_Name column

            df = pd.DataFrame(logs, columns=[
                'Log_ID', 'Station_ID', 'Event_Type', 'Description', 'Severity',
                'Timestamp', 'Station_Name'
            ])

            # Color coding for severity
            def color_severity(val):
                if val == 'critical':
                    return 'background-color: #ffcccc'
                elif val == 'error':
                    return 'background-color: #ffe6cc'
                elif val == 'warning':
                    return 'background-color: #ffffcc'
                else:
                    return ''

            styled_df = df.style.applymap(color_severity, subset=['Severity'])
            st.dataframe(styled_df, use_container_width=True)

            # Summary statistics
            severity_counts = df['Severity'].value_counts()
            st.markdown("### إحصائيات السجلات")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("معلومات", severity_counts.get('info', 0))
            with col2:
                st.metric("تحذيرات", severity_counts.get('warning', 0))
            with col3:
                st.metric("أخطاء", severity_counts.get('error', 0))
            with col4:
                st.metric("حرجة", severity_counts.get('critical', 0))
        else:
            st.info("ℹ️ لا توجد سجلات نظام")

if __name__ == "__main__":
    main()
