"""
Addition Manager - CRUD Operations and Data Management Interfaces

This module handles all addition and CRUD operations for the system.
"""

import streamlit as st
import pandas as pd
from core.database_enhanced import (
    get_all_stations, get_all_pumps, get_all_tanks, get_all_employees,
    get_all_fuel_types, add_petrol_station, add_employee, add_fuel_pump, add_fuel_tank
)


class AdditionManager:
    """Manager for all addition and CRUD operations"""

    def __init__(self):
        """Initialize the addition manager"""
        pass

    def show_addition_interface(self):
        """Display the main addition interface"""
        st.markdown("""
            <style>
            .addition-header {
                background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin: 1rem 0;
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<h1 class="addition-header">➕ الإضافة والإدارة</h1>', unsafe_allow_html=True)

        # Navigation tabs for different addition categories
        addition_tabs = st.tabs([
            "🏭 البنية التحتية",
            "👥 الموظفين",
            "🔗 التعيينات",
            "🧾 العمليات",
            "🔧 الصيانة"
        ])

        with addition_tabs[0]:
            self._infrastructure_addition()

        with addition_tabs[1]:
            self._employees_addition()

        with addition_tabs[2]:
            self._assignments_addition()

        with addition_tabs[3]:
            self._operations_addition()

        with addition_tabs[4]:
            self._maintenance_addition()

    def _infrastructure_addition(self):
        """Manage infrastructure additions"""
        st.markdown("### 🏭 إدارة البنية التحتية")

        infra_tabs = st.tabs(["🏭 المحطات", "⛽ المضخات", "🗂️ الخزانات"])

        with infra_tabs[0]:
            self._stations_addition()

        with infra_tabs[1]:
            self._pumps_addition()

        with infra_tabs[2]:
            self._tanks_addition()

    def _stations_addition(self):
        """Add and manage stations"""
        st.markdown("#### ➕ إضافة محطة جديدة")

        stations = get_all_stations()

        col1, col2 = st.columns([1, 1])

        with col1:
            with st.form("add_station_form"):
                station_id = st.text_input("رقم المحطة", max_chars=10)
                station_name = st.text_input("اسم المحطة", max_chars=100)
                city = st.text_input("المدينة", max_chars=40)

                if st.form_submit_button("🏭 إضافة المحطة", use_container_width=True):
                    if station_id and station_name and city:
                        if add_petrol_station(station_id, station_name, "", "", 2024, "", city, "", "", ""):
                            st.success("✅ تمت إضافة المحطة بنجاح!")
                            st.rerun()
                        else:
                            st.error("❌ خطأ في إضافة المحطة")
                    else:
                        st.error("❌ يرجى ملء الحقول المطلوبة")

        with col2:
            st.markdown("#### 📋 جميع المحطات")
            if stations:
                df = pd.DataFrame(stations, columns=[
                    'Station_ID', 'Station_Name', 'Company_Name', 'Registration_No',
                    'Opening_Year', 'State', 'City', 'Address', 'Phone', 'Manager_ID',
                    'Total_Pumps', 'Total_Tanks', 'Is_Active', 'Created_Date'
                ])
                st.dataframe(df[['Station_ID', 'Station_Name', 'City', 'Is_Active']], use_container_width=True)
            else:
                st.info("ℹ️ لا توجد محطات مسجلة")

    def _pumps_addition(self):
        """Add and manage pumps"""
        st.markdown("#### ➕ إضافة مضخة جديدة")

        stations = get_all_stations()
        fuel_types = get_all_fuel_types()

        col1, col2 = st.columns([1, 1])

        with col1:
            with st.form("add_pump_form"):
                pump_id = st.text_input("رقم المضخة", max_chars=10)
                station_id = st.selectbox("المحطة", [s[0] for s in stations] if stations else [""])
                pump_name = st.text_input("اسم المضخة", max_chars=50)
                fuel_type_id = st.selectbox("نوع الوقود", [ft[0] for ft in fuel_types] if fuel_types else [""])

                if st.form_submit_button("⛽ إضافة المضخة", use_container_width=True):
                    if pump_id and station_id and pump_name and fuel_type_id:
                        if add_fuel_pump(pump_id, station_id, pump_name, 1, "", fuel_type_id, None, None):
                            st.success("✅ تمت إضافة المضخة بنجاح!")
                            st.rerun()
                        else:
                            st.error("❌ خطأ في إضافة المضخة")
                    else:
                        st.error("❌ يرجى ملء الحقول المطلوبة")

        with col2:
            st.markdown("#### 📋 جميع المضخات")
            pumps = get_all_pumps()
            if pumps:
                df = pd.DataFrame(pumps, columns=[
                    'Pump_ID', 'Station_ID', 'Pump_Name', 'Pump_Number', 'Location',
                    'FuelType_ID', 'Tank_ID', 'Employee_ID', 'Max_Flow_Rate',
                    'Is_Active', 'Last_Service', 'Next_Service', 'Total_Liters_Dispensed',
                    'Created_Date', 'Station_Name', 'FuelType_Name', 'Tank_Name', 'Employee_Name'
                ])
                st.dataframe(df[['Pump_Name', 'Station_Name', 'FuelType_Name', 'Is_Active']], use_container_width=True)
            else:
                st.info("ℹ️ لا توجد مضخات مسجلة")

    def _tanks_addition(self):
        """Add and manage tanks"""
        st.markdown("#### ➕ إضافة خزان جديد")

        stations = get_all_stations()
        fuel_types = get_all_fuel_types()

        col1, col2 = st.columns([1, 1])

        with col1:
            with st.form("add_tank_form"):
                tank_id = st.text_input("رقم الخزان", max_chars=10)
                station_id = st.selectbox("المحطة", [s[0] for s in stations] if stations else [""])
                fuel_type_id = st.selectbox("نوع الوقود", [ft[0] for ft in fuel_types] if fuel_types else [""])
                tank_name = st.text_input("اسم الخزان", max_chars=50)
                capacity_liters = st.number_input("السعة (لتر)", min_value=0.0, value=50000.0)

                if st.form_submit_button("🗂️ إضافة الخزان", use_container_width=True):
                    if tank_id and station_id and fuel_type_id and tank_name:
                        if add_fuel_tank(tank_id, station_id, fuel_type_id, tank_name, capacity_liters, 5.0, 1.0, ""):
                            st.success("✅ تمت إضافة الخزان بنجاح!")
                            st.rerun()
                        else:
                            st.error("❌ خطأ في إضافة الخزان")
                    else:
                        st.error("❌ يرجى ملء الحقول المطلوبة")

        with col2:
            st.markdown("#### 📋 جميع الخزانات")
            tanks = get_all_tanks()
            if tanks:
                df = pd.DataFrame(tanks, columns=[
                    'Tank_ID', 'Station_ID', 'FuelType_ID', 'Tank_Name', 'Capacity_Liters',
                    'Current_Amount_Liters', 'Max_Pressure', 'Min_Pressure', 'Location',
                    'Is_Active', 'Last_Maintenance', 'Next_Maintenance', 'Created_Date',
                    'Station_Name', 'FuelType_Name'
                ])
                st.dataframe(df[['Tank_Name', 'Station_Name', 'FuelType_Name', 'Capacity_Liters', 'Is_Active']], use_container_width=True)
            else:
                st.info("ℹ️ لا توجد خزانات مسجلة")

    def _employees_addition(self):
        """Manage employee additions"""
        st.markdown("### 👥 إدارة الموظفين")

        emp_tabs = st.tabs(["➕ إضافة موظف", "📋 جميع الموظفين"])

        with emp_tabs[0]:
            self._add_employee_form()

        with emp_tabs[1]:
            self._view_employees()

    def _add_employee_form(self):
        """Add new employee form"""
        st.markdown("#### ➕ إضافة موظف جديد")

        stations = get_all_stations()

        with st.form("add_employee_form"):
            employee_id = st.text_input("رقم الموظف", max_chars=10)
            emp_name = st.text_input("اسم الموظف", max_chars=50)
            station_id = st.selectbox("المحطة", [s[0] for s in stations] if stations else [""])
            designation = st.selectbox("المنصب", ["مدير محطة", "مشرف", "عامل مضخة", "محاسب"])
            salary = st.number_input("الراتب", min_value=0.0, value=3000.0)

            if st.form_submit_button("👥 إضافة الموظف", use_container_width=True):
                if employee_id and emp_name and station_id:
                    if add_employee(employee_id, station_id, emp_name, "ذ", designation, pd.Timestamp.now().date(), salary, "", "", "", ""):
                        st.success("✅ تمت إضافة الموظف بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في إضافة الموظف")
                else:
                    st.error("❌ يرجى ملء الحقول المطلوبة")

    def _view_employees(self):
        """View all employees"""
        st.markdown("#### 📋 جميع الموظفين")

        employees = get_all_employees()
        if employees:
            df = pd.DataFrame(employees, columns=[
                'Employee_ID', 'Station_ID', 'Emp_Name', 'Emp_Gender', 'Designation',
                'DOB', 'Salary', 'Emp_Address', 'Email_ID', 'Phone', 'Manager_ID',
                'Hire_Date', 'Is_Active', 'Created_Date', 'Station_Name', 'Manager_Name'
            ])
            st.dataframe(df[['Emp_Name', 'Designation', 'Station_Name', 'Salary', 'Is_Active']], use_container_width=True)
        else:
            st.info("ℹ️ لا يوجد موظفون مسجلون")

    def _assignments_addition(self):
        """Manage assignments and linkages"""
        st.markdown("### 🔗 التعيينات والربط")

        # Import and use the assignments module
        from pages.management.main_management_assignments import main as assignments_main
        assignments_main()

    def _operations_addition(self):
        """Manage operations (invoices, supplies)"""
        st.markdown("### 🧾 العمليات والمعاملات")
        st.info("🔄 سيتم تطوير واجهات الفواتير والتوريد قريباً")

    def _maintenance_addition(self):
        """Manage maintenance operations"""
        st.markdown("### 🔧 الصيانة والفحص")
        st.info("🔄 سيتم تطوير واجهات الصيانة قريباً")
