import streamlit as st
import pandas as pd
from core.database_enhanced import (
    get_all_employees, add_employee, get_all_stations, get_all_pumps
)

def main():
    """Main management page for employees"""

    st.title("👥 إدارة الموظفين")

    # Create tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ إضافة موظف",
        "📋 جميع الموظفين",
        "📊 تقارير الموظفين",
        "💰 ديون الموظفين"
    ])

    with tab1:
        add_employee_tab()

    with tab2:
        view_employees_tab()

    with tab3:
        employees_reports_tab()

    with tab4:
        employee_debts_tab()

def add_employee_tab():
    """Add new employee"""
    st.subheader("➕ إضافة موظف جديد")

    # Get stations for dropdown
    stations = get_all_stations()

    with st.form("add_employee_form"):
        col1, col2 = st.columns(2)

        with col1:
            employee_id = st.text_input("رقم الموظف", max_chars=10, help="مثال: EMP001")
            emp_name = st.text_input("اسم الموظف", max_chars=50)
            emp_gender = st.selectbox("الجنس", ["ذكر", "أنثى"], index=0)
            designation = st.selectbox("المنصب", [
                "مدير محطة", "مشرف", "عامل مضخة", "محاسب", "أمين مخزن", "عامل نظافة"
            ])
            dob = st.date_input("تاريخ الميلاد")
            salary = st.number_input("الراتب", min_value=0.0, value=3000.0, step=100.0)

        with col2:
            station_id = st.selectbox(
                "المحطة",
                [s[0] for s in stations] if stations else [""],
                format_func=lambda x: next((s[1] for s in stations if s[0] == x), x) if stations else "لا توجد محطات"
            )
            emp_address = st.text_area("العنوان", height=60)
            email_id = st.text_input("البريد الإلكتروني", max_chars=100)
            phone = st.text_input("رقم الهاتف", max_chars=15)
            manager_id = st.text_input("رقم المدير (اختياري)", max_chars=10)
            hire_date = st.date_input("تاريخ التوظيف", value=pd.Timestamp.now().date())

        if st.form_submit_button("إضافة الموظف", use_container_width=True):
            if employee_id and emp_name and station_id:
                if add_employee(
                    employee_id, station_id, emp_name, emp_gender[0], designation,
                    dob, salary, emp_address, email_id, phone, manager_id
                ):
                    st.success("✅ تمت إضافة الموظف بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ خطأ في إضافة الموظف")
            else:
                st.error("❌ يرجى ملء جميع الحقول المطلوبة")

def view_employees_tab():
    """View all employees"""
    st.subheader("📋 جميع الموظفين")

    employees = get_all_employees()

    if employees:
        df = pd.DataFrame(employees, columns=[
            'Employee_ID', 'Station_ID', 'Emp_Name', 'Emp_Gender', 'Designation',
            'DOB', 'Salary', 'Emp_Address', 'Email_ID', 'Phone', 'Manager_ID',
            'Hire_Date', 'Is_Active', 'Created_Date', 'Station_Name', 'Manager_Name'
        ])

        # Add salary formatting
        df['Salary'] = df['Salary'].apply(lambda x: f"{x:,.0f} ريال" if pd.notna(x) else "غير محدد")

        st.dataframe(df, use_container_width=True)

        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("إجمالي الموظفين", len(employees))

        with col2:
            active_employees = len([e for e in employees if e[12]])  # Is_Active
            st.metric("الموظفون النشطون", active_employees)

        with col3:
            avg_salary = sum(float(e[6]) for e in employees if e[6]) / len([e for e in employees if e[6]])
            st.metric("متوسط الراتب", f"{avg_salary:,.0f} ريال")

        with col4:
            managers = len([e for e in employees if e[4] == "مدير محطة"])
            st.metric("عدد المديرين", managers)

        # Employees by designation
        st.subheader("👔 توزيع الموظفين حسب المنصب")

        designations = {}
        for emp in employees:
            designation = emp[4]  # Designation
            if designation:
                designations[designation] = designations.get(designation, 0) + 1

        if designations:
            des_df = pd.DataFrame(list(designations.items()), columns=['المنصب', 'عدد الموظفين'])
            st.bar_chart(des_df.set_index('المنصب'))
    else:
        st.info("ℹ️ لا يوجد موظفون مسجلون")

def employees_reports_tab():
    """Reports for employees"""
    st.subheader("📊 تقارير الموظفين")

    employees = get_all_employees()
    stations = get_all_stations()

    if not employees:
        st.info("ℹ️ لا توجد بيانات لعرض التقارير")
        return

    # Employees by station
    st.subheader("🏭 الموظفون حسب المحطة")

    station_employees = {}
    for emp in employees:
        station_name = emp[14]  # Station_Name
        if station_name:
            station_employees[station_name] = station_employees.get(station_name, 0) + 1

    if station_employees:
        station_df = pd.DataFrame(list(station_employees.items()), columns=['المحطة', 'عدد الموظفين'])
        st.dataframe(station_df, use_container_width=True)

        # Chart
        st.bar_chart(station_df.set_index('المحطة'))

    # Salary analysis
    st.subheader("💰 تحليل الرواتب")

    salaries = [float(e[6]) for e in employees if e[6]]
    if salaries:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("أعلى راتب", f"{max(salaries):,.0f} ريال")

        with col2:
            st.metric("أقل راتب", f"{min(salaries):,.0f} ريال")

        with col3:
            avg_salary = sum(salaries) / len(salaries)
            st.metric("متوسط الراتب", f"{avg_salary:,.0f} ريال")

        with col4:
            salary_range = max(salaries) - min(salaries)
            st.metric("نطاق الرواتب", f"{salary_range:,.0f} ريال")

    # Employee performance (mock data - in real system would come from actual performance metrics)
    st.subheader("⭐ أداء الموظفين")

    # Create mock performance data based on designation and salary
    performance_data = []
    for emp in employees:
        emp_id = emp[0]
        emp_name = emp[2]
        designation = emp[4]
        salary = float(emp[6]) if emp[6] else 0

        # Mock performance score based on designation and salary level
        base_score = 70
        if designation == "مدير محطة":
            base_score += 20
        elif designation == "مشرف":
            base_score += 15
        elif designation == "محاسب":
            base_score += 10

        if salary > 5000:
            base_score += 10
        elif salary > 3000:
            base_score += 5

        performance_score = min(base_score, 100)

        performance_data.append({
            'الموظف': emp_name,
            'المنصب': designation,
            'الراتب': salary,
            'نقاط الأداء': performance_score,
            'التقييم': get_performance_rating(performance_score)
        })

    if performance_data:
        perf_df = pd.DataFrame(performance_data)
        st.dataframe(perf_df, use_container_width=True)

        # Performance chart
        st.subheader("📈 توزيع نقاط الأداء")
        perf_chart = pd.DataFrame(performance_data)[['الموظف', 'نقاط الأداء']]
        st.bar_chart(perf_chart.set_index('الموظف'))

def get_performance_rating(score):
    """Get performance rating based on score"""
    if score >= 90:
        return "ممتاز ⭐⭐⭐⭐⭐"
    elif score >= 80:
        return "جيد جدا ⭐⭐⭐⭐"
    elif score >= 70:
        return "جيد ⭐⭐⭐"
    elif score >= 60:
        return "مقبول ⭐⭐"
    else:
        return "يحتاج تحسين ⭐"

def employee_debts_tab():
    """Employee debts management tab"""
    st.subheader("💰 إدارة ديون الموظفين")

    from core.database_enhanced import get_pending_debts, get_employee_debts, update_employee_debt_status

    # Get all employees for dropdown
    employees = get_all_employees()

    # Create sub-tabs for different debt operations
    debt_tab1, debt_tab2, debt_tab3 = st.tabs(["➕ إضافة دين جديد", "📋 الديون المعلقة", "🔍 بحث ديون موظف"])

    with debt_tab1:
        st.subheader("➕ إضافة دين جديد")

        # Get all employees for dropdown
        employees_list = get_all_employees()

        if employees_list:
            with st.form("add_debt_form"):
                col1, col2 = st.columns(2)

                with col1:
                    selected_employee = st.selectbox(
                        "اختر الموظف",
                        [f"{e[0]} - {e[2]}" for e in employees_list],
                        format_func=lambda x: x
                    )
                    settlement_date = st.date_input("تاريخ التسوية", value=pd.Timestamp.now().date())
                    sold_quantity = st.number_input("الكمية المباعة (لتر)", min_value=0.0, step=0.1)
                    unit_price = st.number_input("سعر الوحدة (ريال)", min_value=0.0, step=0.01)
                    notes = st.text_area("ملاحظات", height=60)

                with col2:
                    # Calculate owed amount
                    owed_amount = sold_quantity * unit_price
                    st.info(f"**المبلغ المستحق: {owed_amount:,.2f} ريال**")

                    if st.form_submit_button("إضافة الدين", use_container_width=True):
                        if selected_employee and sold_quantity > 0 and unit_price > 0:
                            employee_id = selected_employee.split(' - ')[0]
                            from core.database_enhanced import add_employee_debt
                            if add_employee_debt(
                                employee_id, settlement_date, sold_quantity, unit_price, owed_amount, notes
                            ):
                                st.success("✅ تمت إضافة الدين بنجاح!")
                                st.rerun()
                            else:
                                st.error("❌ خطأ في إضافة الدين")
                        else:
                            st.error("❌ يرجى ملء جميع الحقول المطلوبة")
        else:
            st.info("ℹ️ لا يوجد موظفون مسجلون")

    with debt_tab2:
        st.subheader("📋 الديون المعلقة")

        # Get pending debts
        pending_debts = get_pending_debts()

        if pending_debts:
            # Convert to DataFrame for better display
            df = pd.DataFrame(pending_debts, columns=[
                'Debt_ID', 'Employee_ID', 'Emp_Name', 'Settlement_Date',
                'Sold_Quantity', 'Unit_Price', 'Owed_Amount', 'Status', 'Notes'
            ])

            # Format currency columns
            df['Sold_Quantity'] = df['Sold_Quantity'].apply(lambda x: f"{x:,.2f} لتر" if pd.notna(x) else "غير محدد")
            df['Unit_Price'] = df['Unit_Price'].apply(lambda x: f"{x:,.2f} ريال" if pd.notna(x) else "غير محدد")
            df['Owed_Amount'] = df['Owed_Amount'].apply(lambda x: f"{x:,.2f} ريال" if pd.notna(x) else "غير محدد")

            # Rename columns for Arabic
            df.columns = ['رقم الدين', 'رقم الموظف', 'اسم الموظف', 'تاريخ التسوية',
                         'الكمية المباعة', 'سعر الوحدة', 'المبلغ المستحق', 'الحالة', 'ملاحظات']

            st.dataframe(df, use_container_width=True)

            # Summary statistics
            total_pending = sum(float(d[6]) for d in pending_debts if d[6])
            st.metric("إجمالي الديون المعلقة", f"{total_pending:,.2f} ريال")

            # Settlement actions
            st.subheader("💳 تسوية الديون")

            col1, col2 = st.columns(2)

            with col1:
                selected_debt = st.selectbox(
                    "اختر الدين المراد تسويته",
                    [f"{d[0]} - {d[2]} ({d[6]:,.2f} ريال)" for d in pending_debts],
                    key="settle_debt_select"
                )

            with col2:
                if st.button("✅ تسوية الدين", use_container_width=True):
                    if selected_debt:
                        debt_id = selected_debt.split(' - ')[0]
                        if update_employee_debt_status(debt_id, 'Paid'):
                            st.success("✅ تم تسوية الدين بنجاح!")
                            st.rerun()
                        else:
                            st.error("❌ خطأ في تسوية الدين")
        else:
            st.info("ℹ️ لا توجد ديون معلقة")

    with debt_tab3:
        st.subheader("🔍 بحث ديون موظف")

        # Employee selection
        if employees:
            selected_employee = st.selectbox(
                "اختر الموظف",
                [f"{e[0]} - {e[2]}" for e in employees],
                format_func=lambda x: x,
                key="employee_debt_select"
            )

            if selected_employee:
                employee_id = selected_employee.split(' - ')[0]

                # Get employee debts
                employee_debts = get_employee_debts(employee_id)

                if employee_debts:
                    df = pd.DataFrame(employee_debts, columns=[
                        'Debt_ID', 'Employee_ID', 'Settlement_Date', 'Sold_Quantity',
                        'Unit_Price', 'Owed_Amount', 'Status', 'Notes', 'Created_Date'
                    ])

                    # Format columns
                    df['Sold_Quantity'] = df['Sold_Quantity'].apply(lambda x: f"{x:,.2f} لتر" if pd.notna(x) else "غير محدد")
                    df['Unit_Price'] = df['Unit_Price'].apply(lambda x: f"{x:,.2f} ريال" if pd.notna(x) else "غير محدد")
                    df['Owed_Amount'] = df['Owed_Amount'].apply(lambda x: f"{x:,.2f} ريال" if pd.notna(x) else "غير محدد")

                    # Rename columns
                    df.columns = ['رقم الدين', 'رقم الموظف', 'تاريخ التسوية', 'الكمية المباعة',
                                 'سعر الوحدة', 'المبلغ المستحق', 'الحالة', 'ملاحظات', 'تاريخ الإنشاء']

                    st.dataframe(df, use_container_width=True)

                    # Calculate totals
                    total_debts = len(employee_debts)
                    paid_debts = len([d for d in employee_debts if d[6] == 'Paid'])
                    pending_debts = total_debts - paid_debts
                    total_amount = sum(float(d[5]) for d in employee_debts if d[5])

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("إجمالي الديون", total_debts)

                    with col2:
                        st.metric("الديون المدفوعة", paid_debts)

                    with col3:
                        st.metric("الديون المعلقة", pending_debts)

                    with col4:
                        st.metric("إجمالي المبلغ", f"{total_amount:,.2f} ريال")
                else:
                    st.info("ℹ️ لا توجد ديون لهذا الموظف")
        else:
            st.info("ℹ️ لا يوجد موظفون مسجلون")

if __name__ == "__main__":
    main()
