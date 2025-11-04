import streamlit as st
import pandas as pd
from core.database import *

def show_management_interface():
    """Display main management interface"""
    st.markdown("""
        <style>
        .management-container {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
        }
        .management-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .management-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .management-card:hover {
            transform: translateY(-5px);
            border-color: #0d6efd;
            box-shadow: 0 8px 25px rgba(13,110,253,0.2);
        }
        .management-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .management-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #0d6efd;
            margin-bottom: 1rem;
        }
        .management-description {
            color: #6c757d;
            margin-bottom: 1.5rem;
        }
        .management-button {
            background: linear-gradient(45deg, #0d6efd, #0056b3) !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 0.75rem 2rem !important;
            font-size: 1rem !important;
            font-weight: bold !important;
            width: 100% !important;
            margin-top: 1rem !important;
            transition: all 0.3s ease !important;
        }
        .management-button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 15px rgba(13,110,253,0.3) !important;
        }
        .section-header {
            color: #0d6efd;
            font-size: 2rem;
            font-weight: bold;
            margin: 2rem 0 1rem 0;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="section-header">⚙️ إدارة النظام</h1>', unsafe_allow_html=True)

    st.markdown('<div class="management-grid">', unsafe_allow_html=True)

    # Petrol Pump Management
    st.markdown('''
        <div class="management-card">
            <div class="management-icon">⛽</div>
            <div class="management-title">إدارة محطات الوقود</div>
            <div class="management-description">
                إدارة بيانات محطات الوقود، إضافة وحذف وتعديل المحطات
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("🏪 إدارة محطات الوقود", key="petrol_pump_mgmt", use_container_width=True):
        st.session_state.management_page = "petrol_pump"
        st.rerun()

    # Employee Management
    st.markdown('''
        <div class="management-card">
            <div class="management-icon">👥</div>
            <div class="management-title">إدارة الموظفين</div>
            <div class="management-description">
                إدارة بيانات الموظفين، الصلاحيات، والمسميات الوظيفية
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("👨‍💼 إدارة الموظفين", key="employee_mgmt", use_container_width=True):
        st.session_state.management_page = "employee"
        st.rerun()

    # Customer Management
    st.markdown('''
        <div class="management-card">
            <div class="management-icon">👤</div>
            <div class="management-title">إدارة العملاء</div>
            <div class="management-description">
                إدارة بيانات العملاء، معلومات الاتصال والتفاصيل الشخصية
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("👥 إدارة العملاء", key="customer_mgmt", use_container_width=True):
        st.session_state.management_page = "customer"
        st.rerun()

    # Invoice Management
    st.markdown('''
        <div class="management-card">
            <div class="management-icon">🧾</div>
            <div class="management-title">إدارة الفواتير</div>
            <div class="management-description">
                إدارة فواتير البيع، تتبع المبيعات والمدفوعات
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("🧾 إدارة الفواتير", key="invoice_mgmt", use_container_width=True):
        st.session_state.management_page = "invoice"
        st.rerun()

    # Tanker Management
    st.markdown('''
        <div class="management-card">
            <div class="management-icon">🚛</div>
            <div class="management-title">إدارة الخزانات</div>
            <div class="management-description">
                إدارة خزانات الوقود، مراقبة المخزون والسعة
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("🚛 إدارة الخزانات", key="tanker_mgmt", use_container_width=True):
        st.session_state.management_page = "tanker"
        st.rerun()

    # Owner Management
    st.markdown('''
        <div class="management-card">
            <div class="management-icon">👑</div>
            <div class="management-title">إدارة المالكين</div>
            <div class="management-description">
                إدارة بيانات مالكي محطات الوقود ومعلومات الشراكة
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("👑 إدارة المالكين", key="owner_mgmt", use_container_width=True):
        st.session_state.management_page = "owner"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick Actions
    st.markdown('<h2 class="section-header">⚡ الإجراءات السريعة</h2>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 عرض التقارير", key="quick_reports", use_container_width=True):
            st.session_state.management_page = "reports"
            st.rerun()

    with col2:
        if st.button("🔍 البحث المتقدم", key="quick_search", use_container_width=True):
            st.session_state.management_page = "search"
            st.rerun()

    with col3:
        if st.button("⚙️ إعدادات النظام", key="quick_settings", use_container_width=True):
            st.session_state.management_page = "settings"
            st.rerun()

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

def main():
    """Main management function"""
    # Initialize session state
    if 'management_page' not in st.session_state:
        st.session_state.management_page = None

    # Navigation
    if st.session_state.management_page is None:
        show_management_interface()
    elif st.session_state.management_page == "petrol_pump":
        show_petrol_pump_management()
        if st.button("⬅️ العودة للقائمة الرئيسية", key="back_to_main"):
            st.session_state.management_page = None
            st.rerun()
    elif st.session_state.management_page == "employee":
        show_employee_management()
        if st.button("⬅️ العودة للقائمة الرئيسية", key="back_to_main"):
            st.session_state.management_page = None
            st.rerun()

if __name__ == "__main__":
    main()
