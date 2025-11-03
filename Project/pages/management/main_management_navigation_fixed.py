import streamlit as st
import pandas as pd
from core.database import *
from pages.management.main_management_employee_pump_assignment import main as employee_pump_assignment_main

def show_main_interface():
    """Display simplified main interface with only 3 sections"""
    st.markdown("""
        <style>
        .main-container {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 3rem;
            border-radius: 20px;
            margin: 2rem 0;
            text-align: center;
        }
        .main-title {
            color: #0d6efd;
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 2rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .main-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
            margin: 2rem 0;
        }
        .main-button {
            background: linear-gradient(135deg, #0d6efd 0%, #6610f2 100%);
            color: white;
            border: none;
            padding: 2rem;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        .main-button:hover {
            background: linear-gradient(135deg, #6610f2 0%, #0d6efd 100%);
            transform: translateY(-5px);
            box-shadow: 0 12px 35px rgba(13,110,253,0.3);
        }
        .button-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">🏢 نظام إدارة محطات الوقود</h1>', unsafe_allow_html=True)

    st.markdown('<div class="main-grid">', unsafe_allow_html=True)

    # Management Button
    st.markdown('''
        <button class="main-button" onclick="document.getElementById('management_btn').click()">
            <span class="button-icon">⚙️</span>
            إدارة النظام
        </button>
    ''', unsafe_allow_html=True)

    # Reports Button
    st.markdown('''
        <button class="main-button" onclick="document.getElementById('reports_btn').click()">
            <span class="button-icon">📊</span>
            التقارير
        </button>
    ''', unsafe_allow_html=True)

    # Dashboard Button
    st.markdown('''
        <button class="main-button" onclick="document.getElementById('dashboard_btn').click()">
            <span class="button-icon">📈</span>
            لوحة التحكم
        </button>
    ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Hidden buttons for navigation
    if st.button("⚙️ إدارة النظام", key="management_btn", use_container_width=True):
        st.session_state.main_section = "management"

    if st.button("📊 التقارير", key="reports_btn", use_container_width=True):
        st.session_state.main_section = "reports"

    if st.button("📈 لوحة التحكم", key="dashboard_btn", use_container_width=True):
        st.session_state.main_section = "dashboard"

    # Handle navigation
    if 'main_section' in st.session_state and st.session_state.main_section:
        section = st.session_state.main_section

        if section == "management":
            show_unified_management_interface()
        elif section == "reports":
            st.info("📊 التقارير - سيتم تطوير هذا القسم قريباً")
        elif section == "dashboard":
            st.info("📈 لوحة التحكم - سيتم تطوير هذا القسم قريباً")

def show_unified_management_interface():
    """Display unified management interface with all functions in one place"""
    st.markdown("""
        <style>
        .management-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin: 2rem 0;
        }
        .management-title {
            color: #0d6efd;
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 2rem;
        }
        .management-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .management-button {
            background: linear-gradient(135deg, #0d6efd 0%, #6610f2 100%);
            color: white;
            border: none;
            padding: 1.5rem;
            border-radius: 15px;
            font-weight: 600;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .management-button:hover {
            background: linear-gradient(135deg, #6610f2 0%, #0d6efd 100%);
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(13,110,253,0.2);
        }
        .button-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="management-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="management-title">⚙️ إدارة النظام</h2>', unsafe_allow_html=True)

    st.markdown('<div class="management-grid">', unsafe_allow_html=True)

    # Petrol Pump Management
    st.markdown('''
        <button class="management-button" onclick="document.getElementById('petrol_pump_mgmt').click()">
            <span class="button-icon">⛽</span>
            إدارة محطات الوقود
        </button>
    ''', unsafe_allow_html=True)

    # Employee Management
    st.markdown('''
        <button class="management-button" onclick="document.getElementById('employee_mgmt').click()">
            <span class="button-icon">👥</span>
            إدارة الموظفين
        </button>
    ''', unsafe_allow_html=True)

    # Employee-Pump Assignment
    st.markdown('''
        <button class="management-button" onclick="document.getElementById('employee_pump_assignment').click()">
            <span class="button-icon">🔗</span>
            ربط الموظفين
        </button>
    ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Hidden buttons for management sections
    if st.button("⛽ إدارة محطات الوقود", key="petrol_pump_mgmt"):
        st.session_state.management_section = "petrol_pump"

    if st.button("👥 إدارة الموظفين", key="employee_mgmt"):
        st.session_state.management_section = "employee"

    if st.button("🔗 ربط الموظفين", key="employee_pump_assignment"):
        st.session_state.management_section = "employee_pump_assignment"

    # Handle detailed management sections
    if 'management_section' in st.session_state and st.session_state.management_section:
        section = st.session_state.management_section

        if section == "petrol_pump":
            show_petrol_pump_management()
        elif section == "employee":
            show_employee_management()
        elif section == "employee_pump_assignment":
            employee_pump_assignment_main()

def show_petrol_pump_management():
    """Display petrol pump management interface"""
    st.markdown("""
        <style>
        .content-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin: 2rem 0;
        }
        .section-title {
            color: #0d6efd;
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">⛽ إدارة محطات الوقود</h2>', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)

def show_employee_management():
    """Display employee management interface"""
    st.markdown("""
        <style>
        .content-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin: 2rem 0;
        }
        .section-title {
            color: #0d6efd;
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">👥 إدارة الموظفين</h2>', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main function"""
    if 'management_page' not in st.session_state:
        st.session_state.management_page = None
    if 'previous_page' not in st.session_state:
        st.session_state.previous_page = 'dashboard'

    if st.session_state.management_page is None:
        show_main_interface()
    elif st.session_state.management_page == "petrol_pump":
        show_petrol_pump_management()
        if st.button("⬅️ العودة للقائمة الرئيسية", key="back_to_main"):
            st.session_state.management_page = None
            st.session_state.current_page = st.session_state.previous_page
    elif st.session_state.management_page == "employee":
        show_employee_management()
        if st.button("⬅️ العودة للقائمة الرئيسية", key="back_to_main"):
            st.session_state.management_page = None
            st.session_state.current_page = st.session_state.previous_page
    elif st.session_state.management_page == "employee_pump_assignment":
        employee_pump_assignment_main()
        if st.button("⬅️ العودة للقائمة الرئيسية", key="back_to_main"):
            st.session_state.management_page = None
            st.session_state.current_page = st.session_state.previous_page

if __name__ == "__main__":
    main()
