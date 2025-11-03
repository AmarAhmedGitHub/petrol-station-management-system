import streamlit as st
import pandas as pd
from core.database import *

def show_employee_pump_assignment():
    """Display employee to pump assignment interface"""
    st.markdown('<h2 class="section-header">🔗 ربط الموظفين بمحطات الوقود</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👥 اختيار الموظف")
        # Get all employees
        employees = view_all_Employee_data()
        if employees:
            employee_options = {f"{emp[1]} (ID: {emp[0]})": emp[0] for emp in employees}
            selected_employee_name = st.selectbox("اختر الموظف", list(employee_options.keys()))
            selected_employee_id = employee_options[selected_employee_name]

            # Show employee details
            employee_data = get_all_info_Employee(selected_employee_id)
            if employee_data:
                st.markdown(f"""
                **تفاصيل الموظف:**
                - الاسم: {employee_data[0][1]}
                - المسمى الوظيفي: {employee_data[0][3]}
                - الراتب: {employee_data[0][5]}
                - رقم المحطة الحالي: {employee_data[0][8]}
                """)
        else:
            st.warning("لا يوجد موظفون مسجلون")
            return

    with col2:
        st.markdown("### ⛽ اختيار محطة الوقود")
        # Get all petrol pumps
        pumps = view_all_Petrolpump_data()
        if pumps:
            pump_options = {f"{pump[1]} (رقم التسجيل: {pump[0]})": pump[0] for pump in pumps}
            selected_pump_name = st.selectbox("اختر محطة الوقود", list(pump_options.keys()))
            selected_pump_id = pump_options[selected_pump_name]

            # Show pump details
            pump_data = get_all_info_Petrolpump(selected_pump_id)
            if pump_data:
                st.markdown(f"""
                **تفاصيل المحطة:**
                - اسم المحطة: {pump_data[0][1]}
                - اسم الشركة: {pump_data[0][2]}
                - سنة الافتتاح: {pump_data[0][3]}
                - الولاية: {pump_data[0][4]}
                - المدينة: {pump_data[0][5]}
                """)
        else:
            st.warning("لا توجد محطات وقود مسجلة")
            return

    # Assignment section
    st.markdown("### 🔄 تنفيذ الربط")

    if st.button("🔗 ربط الموظف بالمحطة", type="primary", use_container_width=True):
        # Update employee's pump assignment
        emp_data = get_all_info_Employee(selected_employee_id)
        if emp_data:
            # Update the employee's petrol pump assignment
            if edit_Employee_data(
                emp_data[0][1],  # name
                emp_data[0][2],  # gender
                emp_data[0][3],  # designation
                emp_data[0][4],  # dob
                emp_data[0][5],  # salary
                emp_data[0][6],  # address
                emp_data[0][7],  # email
                selected_pump_id,  # new pump
                emp_data[0][9],  # manager_id
                selected_employee_id  # employee_id
            ):
                st.success(f"✅ تم ربط الموظف {employee_data[0][1]} بمحطة {pump_data[0][1]} بنجاح!")
                st.balloons()
            else:
                st.error("❌ حدث خطأ أثناء ربط الموظف بالمحطة")

    # Show current assignments
    st.markdown("### 📋 الربط الحالي للموظفين")

    if employees and pumps:
        # Create assignment table
        assignments_data = []
        for emp in employees:
            emp_info = get_all_info_Employee(emp[0])
            if emp_info:
                pump_info = get_all_info_Petrolpump(emp_info[0][8]) if emp_info[0][8] else None
                pump_name = pump_info[0][1] if pump_info else "غير محدد"
                assignments_data.append({
                    'رقم الموظف': emp[0],
                    'اسم الموظف': emp[1],
                    'المسمى الوظيفي': emp[3],
                    'محطة الوقود': pump_name,
                    'رقم محطة الوقود': emp_info[0][8] or "غير محدد"
                })

        if assignments_data:
            df = pd.DataFrame(assignments_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("لا توجد ربط حالي للموظفين")

def show_add_pump_interface():
    """Display add new pump interface"""
    st.markdown('<h2 class="section-header">⛽ إضافة محطة وقود جديدة</h2>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
               padding: 2rem; border-radius: 15px; margin: 1rem 0;">
        <h3 style="color: #0d6efd; margin-bottom: 1rem;">📝 نموذج إضافة محطة جديدة</h3>
        <p style="color: #6c757d; margin-bottom: 0;">يرجى ملء جميع الحقول المطلوبة لإضافة محطة وقود جديدة</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("add_new_pump_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**معلومات أساسية:**")
            reg_no = st.text_input("رقم التسجيل *", placeholder="أدخل رقم التسجيل الفريد")
            pump_name = st.text_input("اسم المحطة *", placeholder="أدخل اسم المحطة")
            company_name = st.text_input("اسم الشركة *", placeholder="أدخل اسم الشركة المالكة")
            opening_year = st.number_input("سنة الافتتاح *", min_value=1900, max_value=2025, value=2024)

        with col2:
            st.markdown("**معلومات الموقع:**")
            state = st.text_input("الولاية *", placeholder="أدخل اسم الولاية")
            city = st.text_input("المدينة *", placeholder="أدخل اسم المدينة")

            st.markdown("**معلومات إضافية:**")
            phone = st.text_input("رقم الهاتف", placeholder="أدخل رقم هاتف المحطة (اختياري)")
            address = st.text_area("العنوان التفصيلي", placeholder="أدخل العنوان التفصيلي (اختياري)", height=80)

        # Form submission
        submitted = st.form_submit_button("✅ إضافة المحطة", type="primary", use_container_width=True)

        if submitted:
            # Validation
            if not all([reg_no, pump_name, company_name, state, city]):
                st.error("❌ يرجى ملء جميع الحقول المطلوبة (المحددة بـ *)")
                return

            # Check if registration number already exists
            existing_pumps = view_all_Petrolpump_data()
            if any(pump[0] == reg_no for pump in existing_pumps):
                st.error(f"❌ رقم التسجيل {reg_no} موجود بالفعل. يرجى استخدام رقم مختلف.")
                return

            # Add the pump
            if add_Petrolpump_data(reg_no, pump_name, company_name, opening_year, state, city):
                st.success("✅ تمت إضافة المحطة بنجاح!")
                st.balloons()

                # Show added pump details
                st.markdown(f"""
                **تم إضافة المحطة التالية:**
                - رقم التسجيل: {reg_no}
                - اسم المحطة: {pump_name}
                - اسم الشركة: {company_name}
                - سنة الافتتاح: {opening_year}
                - الولاية: {state}
                - المدينة: {city}
                """)

                if phone:
                    st.markdown(f"- رقم الهاتف: {phone}")
                if address:
                    st.markdown(f"- العنوان: {address}")
            else:
                st.error("❌ حدث خطأ أثناء إضافة المحطة. يرجى المحاولة مرة أخرى.")

def main():
    """Main function for employee-pump assignment and add pump interfaces"""
    st.markdown("""
        <style>
        .section-header {
            color: #0d6efd;
            font-size: 2.5rem;
            font-weight: bold;
            margin: 2rem 0 1rem 0;
            text-align: center;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .content-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin: 2rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Navigation tabs
    tab1, tab2 = st.tabs(["🔗 ربط الموظفين بمحطات الوقود", "⛽ إضافة محطة جديدة"])

    with tab1:
        show_employee_pump_assignment()

    with tab2:
        show_add_pump_interface()

if __name__ == "__main__":
    main()
