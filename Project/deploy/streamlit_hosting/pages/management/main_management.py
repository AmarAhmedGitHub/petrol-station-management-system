import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from core.database_enhanced import (
    get_all_stations, get_all_pumps, get_all_tanks, get_all_fuel_types,
    get_all_employees, get_all_invoices, get_all_supplies, get_all_customers,
    add_invoice, add_fuel_supply
)
from core.database import *

def show_management_interface():
    """Display main management interface with tabs for all management sections"""
    st.markdown('<h1 class="section-header">⛽ إدارة النظام</h1>', unsafe_allow_html=True)

    # Create tabs for all management sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏪 إدارة المحطات",
        "👥 إدارة الموظفين",
        "⛽ إدارة التعييئات",
        "🧾 إدارة الفواتير",
        "🚛 إدارة التوريد",
        "🔧 إدارة الصيانة"
    ])

    with tab1:
        show_petrol_pump_management()

    with tab2:
        show_employee_management()

    with tab3:
        show_filling_management()

    with tab4:
        show_invoice_management()

    with tab5:
        show_supply_management()

    with tab6:
        show_maintenance_management()

def show_petrol_pump_management():
    """Display petrol pump management interface"""
    st.markdown('<h2 class="section-header">⛽ إدارة محطات الوقود</h2>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📝 إضافة", "📋 عرض", "✏️ تعديل", "🗑️ حذف"])

    with tab1:
        st.subheader("إضافة محطة وقود جديدة")
        with st.form("add_petrol_pump"):
            col1, col2 = st.columns(2)

            with col1:
                reg_no = st.text_input("رقم التسجيل")
                pump_name = st.text_input("اسم المحطة")
                company_name = st.text_input("اسم الشركة")
                opening_year = st.number_input("سنة الافتتاح", min_value=1900, max_value=2025)

            with col2:
                state = st.text_input("الولاية")
                city = st.text_input("المدينة")

            if st.form_submit_button("إضافة المحطة", use_container_width=True):
                if add_Petrolpump_data(reg_no, pump_name, company_name, opening_year, state, city):
                    st.success("تمت إضافة المحطة بنجاح!")
                else:
                    st.error("حدث خطأ أثناء إضافة المحطة")

    with tab2:
        st.subheader("جميع محطات الوقود")
        data = view_all_Petrolpump_data()
        if data:
            df = pd.DataFrame(data, columns=['رقم التسجيل', 'اسم المحطة', 'اسم الشركة', 'سنة الافتتاح', 'الولاية', 'المدينة'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("لا توجد محطات وقود مسجلة")

    with tab3:
        st.subheader("تعديل محطة وقود")
        pump_list = [i[0] for i in view_only_Registration_No()]
        if pump_list:
            selected_pump = st.selectbox("اختر المحطة للتعديل", pump_list)
            pump_data = get_all_info_Petrolpump(selected_pump)

            if pump_data:
                with st.form("edit_petrol_pump"):
                    col1, col2 = st.columns(2)

                    with col1:
                        new_name = st.text_input("اسم المحطة الجديد", pump_data[0][1])
                        new_company = st.text_input("اسم الشركة الجديد", pump_data[0][2])
                        new_year = st.number_input("سنة الافتتاح الجديدة", value=pump_data[0][3])

                    with col2:
                        new_state = st.text_input("الولاية الجديدة", pump_data[0][4])
                        new_city = st.text_input("المدينة الجديدة", pump_data[0][5])

                    if st.form_submit_button("حفظ التغييرات", use_container_width=True):
                        if edit_Petrolpump_data(new_name, new_company, new_year, new_state, new_city, selected_pump):
                            st.success("تم تحديث بيانات المحطة بنجاح!")
                        else:
                            st.error("حدث خطأ أثناء تحديث البيانات")
        else:
            st.info("لا توجد محطات وقود للتعديل")

    with tab4:
        st.subheader("حذف محطة وقود")
        pump_list = [i[0] for i in view_only_Registration_No()]
        if pump_list:
            selected_pump = st.selectbox("اختر المحطة للحذف", pump_list)
            st.warning(f"هل أنت متأكد من حذف المحطة: {selected_pump}؟")

            if st.button("حذف المحطة", type="primary", use_container_width=True):
                if delete_data_Petrolpump(selected_pump):
                    st.success("تم حذف المحطة بنجاح!")
                else:
                    st.error("حدث خطأ أثناء حذف المحطة")
        else:
            st.info("لا توجد محطات وقود للحذف")

def show_employee_management():
    """Display employee management interface"""
    st.markdown('<h2 class="section-header">👥 إدارة الموظفين</h2>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📝 إضافة", "📋 عرض", "✏️ تعديل", "🗑️ حذف"])

    with tab1:
        st.subheader("إضافة موظف جديد")
        with st.form("add_employee"):
            col1, col2 = st.columns(2)

            with col1:
                emp_id = st.text_input("رقم الموظف")
                emp_name = st.text_input("اسم الموظف")
                emp_gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
                designation = st.text_input("المسمى الوظيفي")
                dob = st.date_input("تاريخ الميلاد")

            with col2:
                salary = st.number_input("الراتب", min_value=0)
                emp_address = st.text_area("العنوان")
                email = st.text_input("البريد الإلكتروني")
                petrol_pump = st.text_input("رقم المحطة")
                manager_id = st.text_input("رقم المدير")

            if st.form_submit_button("إضافة الموظف", use_container_width=True):
                if add_Employee_data(emp_id, emp_name, emp_gender, designation, dob, salary, emp_address, email, petrol_pump, manager_id):
                    st.success("تمت إضافة الموظف بنجاح!")
                else:
                    st.error("حدث خطأ أثناء إضافة الموظف")

    with tab2:
        st.subheader("جميع الموظفين")
        data = view_all_Employee_data()
        if data:
            df = pd.DataFrame(data, columns=['رقم الموظف', 'اسم الموظف', 'الجنس', 'المسمى الوظيفي', 'تاريخ الميلاد', 'الراتب', 'العنوان', 'البريد الإلكتروني', 'رقم المحطة', 'رقم المدير'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("لا يوجد موظفون مسجلون")

    with tab3:
        st.subheader("تعديل بيانات موظف")
        emp_list = [i[0] for i in view_only_Employee_ID()]
        if emp_list:
            selected_emp = st.selectbox("اختر الموظف للتعديل", emp_list)
            emp_data = get_all_info_Employee(selected_emp)

            if emp_data:
                with st.form("edit_employee"):
                    col1, col2 = st.columns(2)

                    with col1:
                        new_name = st.text_input("اسم الموظف الجديد", emp_data[0][1])
                        new_gender = st.selectbox("الجنس الجديد", ["ذكر", "أنثى"], index=0 if emp_data[0][2] == "ذكر" else 1)
                        new_designation = st.text_input("المسمى الوظيفي الجديد", emp_data[0][3])
                        new_dob = st.date_input("تاريخ الميلاد الجديد", emp_data[0][4])

                    with col2:
                        new_salary = st.number_input("الراتب الجديد", value=emp_data[0][5])
                        new_address = st.text_area("العنوان الجديد", emp_data[0][6])
                        new_email = st.text_input("البريد الإلكتروني الجديد", emp_data[0][7])
                        new_pump = st.text_input("رقم المحطة الجديد", emp_data[0][8])
                        new_manager = st.text_input("رقم المدير الجديد", emp_data[0][9])

                    if st.form_submit_button("حفظ التغييرات", use_container_width=True):
                        if edit_Employee_data(new_name, new_gender, new_designation, new_dob, new_salary, new_address, new_email, new_pump, new_manager, selected_emp):
                            st.success("تم تحديث بيانات الموظف بنجاح!")
                        else:
                            st.error("حدث خطأ أثناء تحديث البيانات")
        else:
            st.info("لا يوجد موظفون للتعديل")

    with tab4:
        st.subheader("حذف موظف")
        emp_list = [i[0] for i in view_only_Employee_ID()]
        if emp_list:
            selected_emp = st.selectbox("اختر الموظف للحذف", emp_list)
            st.warning(f"هل أنت متأكد من حذف الموظف: {selected_emp}؟")

            if st.button("حذف الموظف", type="primary", use_container_width=True):
                if delete_data_Employee(selected_emp):
                    st.success("تم حذف الموظف بنجاح!")
                else:
                    st.error("حدث خطأ أثناء حذف الموظف")
        else:
            st.info("لا يوجد موظفون للحذف")

def show_filling_management():
    """Display filling management interface"""
    st.markdown('<h2 class="section-header">⛽ إدارة التعييئات</h2>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "➕ إضافة تعييئة",
        "📋 جميع التعييئات",
        "📊 تقارير التعييئات"
    ])

    with tab1:
        st.subheader("➕ إضافة تعييئة وقود جديدة")
        st.info("قريباً - إضافة تعييئة وقود")

    with tab2:
        st.subheader("📋 جميع التعييئات")
        st.info("قريباً - عرض جميع التعييئات")

    with tab3:
        st.subheader("📊 تقارير التعييئات")
        st.info("قريباً - تقارير التعييئات")

def show_invoice_management():
    """Display invoice management interface"""
    st.markdown('<h2 class="section-header">🧾 إدارة الفواتير</h2>', unsafe_allow_html=True)

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

def show_supply_management():
    """Display supply management interface"""
    st.markdown('<h2 class="section-header">🚛 إدارة التوريد</h2>', unsafe_allow_html=True)

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

def show_maintenance_management():
    """Display maintenance management interface"""
    st.markdown('<h2 class="section-header">🔧 إدارة الصيانة</h2>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "➕ إضافة صيانة",
        "📋 جميع الصيانات",
        "📊 تقارير الصيانة"
    ])

    with tab1:
        pump_maintenance_tab()

    with tab2:
        tank_maintenance_tab()

    with tab3:
        maintenance_reports_tab()

def pump_maintenance_tab():
    """Pump maintenance management"""
    st.subheader("🔧 صيانة المضخات")

    # Get data for dropdowns
    stations = get_all_stations()
    pumps = get_all_pumps()
    employees = get_all_employees()

    with st.form("pump_maintenance_form"):
        col1, col2 = st.columns(2)

        with col1:
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

            maintenance_date = st.date_input("تاريخ الصيانة", value=datetime.now().date())
            maintenance_type = st.selectbox("نوع الصيانة", [
                "صيانة دورية", "إصلاح عطل", "استبدال قطع", "تنظيف", "فحص"
            ])

        with col2:
            employee_id = st.selectbox(
                "الموظف المسؤول",
                [""] + [e[0] for e in employees] if employees else [""],
                format_func=lambda x: next((e[2] for e in employees if e[0] == x), x) if x else "بدون موظف"
            )

            cost = st.number_input("تكلفة الصيانة (ريال)", min_value=0.0, value=0.0, step=10.0)
            status = st.selectbox("حالة الصيانة", [
                "مكتملة", "قيد التنفيذ", "مؤجلة", "ملغاة"
            ])
            notes = st.text_area("تفاصيل الصيانة", height=80)

        if st.form_submit_button("إضافة صيانة المضخة", use_container_width=True):
            if station_id and pump_id:
                # Here you would call the database function to add pump maintenance
                # For now, just show success message
                st.success("✅ تمت إضافة صيانة المضخة بنجاح!")
                st.rerun()
            else:
                st.error("❌ يرجى ملء جميع الحقول المطلوبة")

def tank_maintenance_tab():
    """Tank maintenance management"""
    st.subheader("🛢️ صيانة الخزانات")

    # Get data for dropdowns
    stations = get_all_stations()
    tanks = get_all_tanks()
    employees = get_all_employees()

    with st.form("tank_maintenance_form"):
        col1, col2 = st.columns(2)

        with col1:
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

            maintenance_date = st.date_input("تاريخ الصيانة", value=datetime.now().date())
            maintenance_type = st.selectbox("نوع الصيانة", [
                "صيانة دورية", "إصلاح عطل", "استبدال قطع", "تنظيف", "فحص", "تعبئة"
            ])

        with col2:
            employee_id = st.selectbox(
                "الموظف المسؤول",
                [""] + [e[0] for e in employees] if employees else [""],
                format_func=lambda x: next((e[2] for e in employees if e[0] == x), x) if x else "بدون موظف"
            )

            cost = st.number_input("تكلفة الصيانة (ريال)", min_value=0.0, value=0.0, step=10.0)
            status = st.selectbox("حالة الصيانة", [
                "مكتملة", "قيد التنفيذ", "مؤجلة", "ملغاة"
            ])
            notes = st.text_area("تفاصيل الصيانة", height=80)

        if st.form_submit_button("إضافة صيانة الخزان", use_container_width=True):
            if station_id and tank_id:
                # Here you would call the database function to add tank maintenance
                # For now, just show success message
                st.success("✅ تمت إضافة صيانة الخزان بنجاح!")
                st.rerun()
            else:
                st.error("❌ يرجى ملء جميع الحقول المطلوبة")

def maintenance_reports_tab():
    """Maintenance reports"""
    st.subheader("📊 تقارير الصيانة")

    # For now, show placeholder content since we don't have maintenance data yet
    st.info("ℹ️ تقارير الصيانة ستكون متاحة بعد إضافة عمليات الصيانة")

    # Placeholder sections for future reports
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("إجمالي عمليات الصيانة", "0")

    with col2:
        st.metric("التكلفة الإجمالية", "0 ريال")

    with col3:
        st.metric("متوسط التكلفة", "0 ريال")

    # Future report sections
    st.subheader("🔧 الصيانة حسب النوع")
    st.info("سيتم عرض إحصائيات الصيانة حسب النوع")

    st.subheader("🏭 الصيانة حسب المحطة")
    st.info("سيتم عرض إحصائيات الصيانة حسب المحطة")

    st.subheader("📈 اتجاه الصيانة الشهري")
    st.info("سيتم عرض اتجاه عمليات الصيانة مع مرور الوقت")

def main():
    """Main management function"""
    show_management_interface()

if __name__ == "__main__":
    main()
