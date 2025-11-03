import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

from create import *
from database import *
from delete import *
from read import *
from update import *

# Import enhanced pages
from pages.management.main_management_stations import main as management_stations
from pages.management.main_management_fuel_types import main as management_fuel_types
from pages.management.main_management_employees import main as management_employees
from pages.management.main_management_invoices import main as management_invoices
from pages.management.main_management_supply import main as management_supply
from pages.management.main_management_maintenance import main as management_maintenance
from pages.reports.main_reports_enhanced import main as reports_enhanced

def main():
    # Enhanced fuel price editor (Admin/Owner only)
    def fuel_price_editor():
        import database
        st.subheader(":money_with_wings: تعديل أسعار أنواع الوقود")
        database.c.execute("SELECT DISTINCT Fuel_Name, Fuel_Price FROM Tanker")
        fuels = database.c.fetchall()
        if not fuels:
            st.info("لا توجد أنواع وقود مسجلة.")
            return
        for fuel, price in fuels:
            col1, col2, col3 = st.columns([2,2,1])
            with col1:
                st.write(f"**{fuel}**")
            with col2:
                new_price = st.number_input(f"سعر {fuel}", value=price or 0.0, min_value=0.0, key=f"price_{fuel}")
            with col3:
                if st.button(f"حفظ السعر", key=f"save_{fuel}"):
                    database.c.execute("UPDATE Tanker SET Fuel_Price=%s WHERE Fuel_Name=%s", (new_price, fuel))
                    database.mydb.commit()
                    st.success(f"تم تحديث سعر {fuel} إلى {new_price}")
                    st.rerun()

    # Enhanced employee permissions (Admin only)
    if "user_type" in st.session_state and st.session_state.user_type == "Admin":
        if 'show_emp_perms' not in st.session_state:
            st.session_state.show_emp_perms = False
        if st.sidebar.button("تحديد صلاحيات الموظفين", key="set_emp_perms"):
            st.session_state.show_emp_perms = True
        if st.session_state.show_emp_perms:
            st.header(":key: تحديد صلاحيات الموظفين")
            import database
            emps = database.view_all_Employee_data()
            emp_options = {f"{e[1]} (ID: {e[0]})": e[0] for e in emps}
            emp_choice = st.selectbox("اختر الموظف", list(emp_options.keys()))
            all_perms = ["Invoice", "Customer", "Query", "Supply", "PumpDirectory", "Report", "Management", "Maintenance"]
            database.c.execute("SELECT Permission FROM EmployeePermissions WHERE Employee_ID=%s", (emp_options[emp_choice],))
            current_perms = [row[0] for row in database.c.fetchall()]
            selected_perms = st.multiselect("حدد الصلاحيات للموظف", all_perms, default=current_perms or all_perms)
            col1, col2 = st.columns([1,1])
            with col1:
                if st.button("حفظ الصلاحيات"):
                    database.c.execute("DELETE FROM EmployeePermissions WHERE Employee_ID=%s", (emp_options[emp_choice],))
                    for perm in selected_perms:
                        database.c.execute("INSERT INTO EmployeePermissions (Employee_ID, Permission) VALUES (%s, %s)", (emp_options[emp_choice], perm))
                    database.mydb.commit()
                    st.success(f"تم حفظ الصلاحيات للموظف {emp_choice}.")
                    st.session_state.show_emp_perms = False
                    st.rerun()
            with col2:
                if st.button("رجوع", key="back_emp_perms"):
                    st.session_state.show_emp_perms = False
                    st.rerun()
            st.stop()

    # Password reset interface
    if st.sidebar.button("نسيت كلمة المرور؟", key="reset_pw_btn"):
        st.header(":unlock: إعادة تعيين كلمة المرور")
        reset_user = st.text_input("اسم المستخدم")
        reset_type = st.selectbox("نوع الحساب", ["Owner", "Employee"])
        security_answer = st.text_input("ما هو اسم مدينتك؟ (سؤال أمان)")
        new_pw = st.text_input("كلمة المرور الجديدة", type="password")
        confirm_pw = st.text_input("تأكيد كلمة المرور الجديدة", type="password")
        import database
        if st.button("تغيير كلمة المرور"):
            if new_pw != confirm_pw:
                st.error("كلمتا المرور غير متطابقتين.")
                st.stop()
            if reset_type == "Owner":
                database.c.execute("SELECT City FROM Owners WHERE Owner_Name=%s", (reset_user,))
                row = database.c.fetchone()
                if row and row[0] and security_answer.strip().lower() == row[0].strip().lower():
                    database.c.execute("UPDATE Owners SET Contact_NO=%s WHERE Owner_Name=%s", (new_pw, reset_user))
                    database.mydb.commit()
                    st.success("تم تغيير كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول.")
                else:
                    st.error("إجابة سؤال الأمان غير صحيحة أو المستخدم غير موجود.")
            else:
                database.c.execute("SELECT City FROM Employee WHERE Emp_Name=%s", (reset_user,))
                row = database.c.fetchone()
                if row and row[0] and security_answer.strip().lower() == row[0].strip().lower():
                    database.c.execute("UPDATE Employee SET Employee_ID=%s WHERE Emp_Name=%s", (new_pw, reset_user))
                    database.mydb.commit()
                    st.success("تم تغيير كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول.")
                else:
                    st.error("إجابة سؤال الأمان غير صحيحة أو المستخدم غير موجود.")
        st.stop()

    # Enhanced styling
    st.markdown("""
        <style>
        .main-title {
            font-size: 2.8em;
            font-weight: bold;
            color: #0d6efd;
            text-align: center;
            margin-bottom: 20px;
        }
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        .stButton button {
            width: 100%;
            margin: 2px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="main-title">⛽ نظام إدارة محطات الوقود المحسن</div>', unsafe_allow_html=True)

    # Login interface
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.username = ''
        st.session_state.permissions = []

    # Account lock logic
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'locked_until' not in st.session_state:
        st.session_state.locked_until = None

    now = datetime.now()
    if st.session_state.locked_until and now < st.session_state.locked_until:
        st.sidebar.error(f"تم قفل الحساب مؤقتاً بسبب تكرار المحاولات الخاطئة. الرجاء المحاولة بعد {st.session_state.locked_until.strftime('%H:%M:%S')}")
        st.stop()

    if not st.session_state.logged_in:
        st.markdown("""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh;'>
                <img src='https://img.icons8.com/color/120/000000/gas-pump.png' width='120' style='margin-bottom: 1em;'>
                <h2 style='color:#0d6efd; margin-bottom: 0.5em;'>تسجيل الدخول</h2>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            st.write("")
            username = st.text_input("اسم المستخدم", key="login_user")
            password = st.text_input("كلمة المرور", type="password", key="login_pass")
            login_btn = st.form_submit_button("تسجيل الدخول")
            login_error = False
            import database
            if login_btn:
                if st.session_state.locked_until and now < st.session_state.locked_until:
                    st.error(f"تم قفل الحساب مؤقتاً. الرجاء المحاولة بعد {st.session_state.locked_until.strftime('%H:%M:%S')}")
                    st.stop()
                if username == "admin" and password == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.user_type = "Admin"
                    st.session_state.username = username
                    st.session_state.permissions = ["ALL"]
                    st.success("تم تسجيل الدخول كمسؤول النظام (Admin)!")
                else:
                    database.c.execute("SELECT * FROM Owners WHERE Owner_Name=%s AND Contact_NO=%s", (username, password))
                    owner = database.c.fetchone()
                    if owner:
                        st.session_state.logged_in = True
                        st.session_state.user_type = "Owner"
                        st.session_state.username = username
                        st.session_state.permissions = ["ALL"]
                        st.success("تم تسجيل الدخول كمالك بنجاح!")
                    else:
                        database.c.execute("SELECT * FROM Employee WHERE Emp_Name=%s AND Employee_ID=%s", (username, password))
                        emp = database.c.fetchone()
                        if emp:
                            st.session_state.logged_in = True
                            st.session_state.user_type = "Employee"
                            st.session_state.username = username
                            database.c.execute("SELECT Permission FROM EmployeePermissions WHERE Employee_ID=%s", (emp[0],))
                            perms = [row[0] for row in database.c.fetchall()]
                            if not perms:
                                perms = ["Invoice", "Customer", "Query"]
                            st.session_state.permissions = perms
                            st.success("تم تسجيل الدخول كموظف بنجاح!")
                        else:
                            login_error = True
                if login_error:
                    st.session_state.login_attempts += 1
                    if st.session_state.login_attempts >= 5:
                        st.session_state.locked_until = now + datetime.timedelta(minutes=2)
                        st.error("تم قفل الحساب مؤقتاً لمدة دقيقتين بسبب تكرار المحاولات الخاطئة.")
                        st.stop()
                    else:
                        st.error(f"بيانات الدخول غير صحيحة! (محاولة {st.session_state.login_attempts}/5)")
                else:
                    st.session_state.login_attempts = 0
                    st.session_state.locked_until = None
                    st.rerun()

    # After login - Enhanced sidebar
    st.sidebar.image("https://img.icons8.com/color/96/000000/gas-pump.png", width=80)
    st.sidebar.markdown(f"<h2 style='color:#0d6efd;'>لوحة التحكم ({st.session_state.user_type})</h2>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<b>مرحباً، {st.session_state.username}!</b>", unsafe_allow_html=True)

    # Welcome message
    if st.session_state.user_type == "Admin":
        st.success("مرحباً بك، مسؤول النظام (Admin). لديك جميع الصلاحيات.")
    elif st.session_state.user_type == "Owner":
        st.success(f"مرحباً بك، المالك {st.session_state.username}. لديك جميع الصلاحيات.")
    elif st.session_state.user_type == "Employee":
        st.info(f"مرحباً بك، الموظف {st.session_state.username}. لديك صلاحيات محدودة حسب الإعدادات.")

    if st.sidebar.button("تسجيل الخروج", key="logout"):
        for k in ["logged_in", "user_type", "username", "show_emp_perms"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    # Enhanced main sections
    main_sections = ["🏠 الواجهة الرئيسية", "📊 لوحة التحكم", "⚙️ الإدارة", "📑 التقارير"]
    section = st.sidebar.radio("الأقسام الرئيسية:", main_sections)

    if "الواجهة الرئيسية" in section:
        # Basic CRUD operations
        menu_icons = {
            "Dashboard": ("لوحة التحكم", "📊", "https://img.icons8.com/color/48/000000/combo-chart--v2.png"),
            "PetrolPump": ("الطرمبات", "⛽", "https://img.icons8.com/color/48/000000/gas-pump.png"),
            "Owners": ("الملاك", "👤", "https://img.icons8.com/color/48/000000/administrator-male.png"),
            "Employee": ("الموظفون", "🧑‍💼", "https://img.icons8.com/color/48/000000/conference-call.png"),
            "Customer": ("العملاء", "👥", "https://img.icons8.com/color/48/000000/group.png"),
            "Invoice": ("الفواتير", "🧾", "https://img.icons8.com/color/48/000000/invoice.png"),
            "Tanker": ("الخزانات", "🚚", "https://img.icons8.com/color/48/000000/oil-tanker-truck.png"),
            "Query": ("استعلامات", "🔍", "https://img.icons8.com/color/48/000000/search--v1.png")
        }

        if st.session_state.user_type == "Admin":
            menu = ["Dashboard", "PetrolPump", "Owners", "Employee", "Customer", "Invoice", "Tanker", "Query", "FuelPriceEditor"]
        elif st.session_state.user_type == "Owner":
            menu = ["Dashboard", "PetrolPump", "Owners", "Employee", "Customer", "Invoice", "Tanker", "Query", "FuelPriceEditor"]
        elif st.session_state.user_type == "Employee":
            perms = st.session_state.permissions
            menu = ["Dashboard"]
            if "Invoice" in perms:
                menu.append("Invoice")
            if "Customer" in perms:
                menu.append("Customer")
            if "Query" in perms:
                menu.append("Query")
        else:
            menu = ["Dashboard"]

        menu_labels = [f"{menu_icons[m][1]} {menu_icons[m][0]}" if m in menu_icons else ("💲 تعديل أسعار الوقود" if m=="FuelPriceEditor" else m) for m in menu]
        choice_idx = st.sidebar.selectbox("القائمة الر يسية", range(len(menu)), format_func=lambda i: menu_labels[i])
        choice = menu[choice_idx]

        if choice in menu_icons:
            st.image(menu_icons[choice][2], width=60)
            st.markdown(f"<h2 style='color:#0d6efd; display:inline;'>{menu_icons[choice][1]} {menu_icons[choice][0]}</h2>", unsafe_allow_html=True)
            st.markdown("<hr style='margin-top:0.5em; margin-bottom:1em;'>", unsafe_allow_html=True)

        if choice == "FuelPriceEditor":
            fuel_price_editor()
            st.stop()

        # Handle CRUD operations
        if choice == "Dashboard":
            st.subheader(":bar_chart: Dashboard")
            import database
            # Get dashboard stats
            database.c.execute("SELECT IFNULL(SUM(Total_Price),0) FROM Invoice")
            total_sales = database.c.fetchone()[0]
            database.c.execute("SELECT COUNT(*) FROM Customer")
            customer_count = database.c.fetchone()[0]
            database.c.execute("SELECT IFNULL(SUM(Fuel_Amount),0) FROM Invoice")
            total_fuel = database.c.fetchone()[0]

            st.markdown(f"""
                <div style='display: flex; gap: 2em;'>
                    <div style='background: #e3f2fd; padding: 1.5em; border-radius: 10px; min-width: 180px;'>
                        <h3 style='color:#0d6efd;'>إجمالي المبيعات</h3>
                        <h2 style='color:#212529;'>{total_sales:,.0f}</h2>
                    </div>
                    <div style='background: #e8f5e9; padding: 1.5em; border-radius: 10px; min-width: 180px;'>
                        <h3 style='color:#388e3c;'>عدد العملاء</h3>
                        <h2 style='color:#212529;'>{customer_count}</h2>
                    </div>
                    <div style='background: #fff3e0; padding: 1.5em; border-radius: 10px; min-width: 180px;'>
                        <h3 style='color:#f57c00;'>كمية الوقود المباعة</h3>
                        <h2 style='color:#212529;'>{total_fuel:,.0f}</h2>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # إخفاء عرض تفاصيل الخزانات في الواجهة الرئيسية حسب طلب المستخدم
            # st.success("تم جلب الإحصائيات بنجاح من قاعدة البيانات.")
            return

        # Handle other CRUD operations
        menu = ["Add", "View", "Update", "Remove"]
        choice2 = st.sidebar.selectbox("CRUD Operations", menu)

        if choice == "PetrolPump":
            if choice2 == "Add":
                st.subheader("Enter Petrolpump Details:")
                create_for_Petrolpump()
            elif choice2 == "View":
                st.subheader("View the Petrolpump details:")
                read_for_Petrolpump()
            elif choice2 == "Update":
                st.subheader("Updated petrolpump tasks")
                update_for_Petrolpump()
            elif choice2 == "Remove":
                st.subheader("Deleted petrolpump tasks")
                delete_for_Petrolpump()

        elif choice == "Owners":
            if choice2 == "Add":
                st.subheader("Enter Owners Details:")
                create_for_Owners()
            elif choice2 == "View":
                st.subheader("View Owners details:")
                read_for_Owners()
            elif choice2 == "Update":
                st.subheader("Update created tasks")
                update_for_Owners()
            elif choice2 == "Remove":
                st.subheader("Delete created tasks")
                delete_for_Owners()

        elif choice == "Employee":
            if choice2 == "Add":
                st.subheader("Enter Employee Details:")
                create_for_Employee()
            elif choice2 == "View":
                st.subheader("View the Employee details:")
                read_for_Employee()
            elif choice2 == "Update":
                st.subheader("Update created tasks")
                update_for_Employee()
            elif choice2 == "Remove":
                st.subheader("Delete created tasks")
                delete_for_Employee()

        elif choice == "Customer":
            if choice2 == "Add":
                st.subheader("Enter Customer Details:")
                create_for_Customer()
            elif choice2 == "View":
                st.subheader("View the Customer details:")
                read_for_Customer()
            elif choice2 == "Update":
                st.subheader("Update created tasks")
                update_for_Customer()
            elif choice2 == "Remove":
                st.subheader("Delete created tasks")
                delete_for_Customer()

        elif choice == "Invoice":
            if choice2 == "Add":
                st.subheader("Enter Invoice Details:")
                create_for_Invoice()
            elif choice2 == "View":
                st.subheader("View the Invoice details:")
                read_for_Invoice()
            elif choice2 == "Update":
                st.subheader("Update created tasks")
                update_for_Invoice()
            elif choice2 == "Remove":
                st.subheader("Delete created tasks")
                delete_for_Invoice()

        elif choice == "Tanker":
            if choice2 == "Add":
                st.subheader("Enter Tanker Details:")
                create_for_Tanker()
            elif choice2 == "View":
                st.subheader("View the Tanker details:")
                read_for_Tanker()
            elif choice2 == "Update":
                st.subheader("Update created tasks")
                update_for_Tanker()
            elif choice2 == "Remove":
                st.subheader("Delete created tasks")
                delete_for_Tanker()

        elif choice == "Query":
            if choice2 == "Custom Query":
                query = st.text_input("Enter Your Query:")
                if st.button("Run Query"):
                    c.execute(query)
                    data = c.fetchall()
                    st.dataframe(data)
            elif choice2 == "Function":
                net_value()

    elif "لوحة التحكم" in section:
        # Enhanced dashboard
        st.header("📊 لوحة التحكم المحسنة")

        # Get enhanced stats
        import database
        database.c.execute("SELECT IFNULL(SUM(Total_Price),0) FROM Invoice")
        total_sales = database.c.fetchone()[0]
        database.c.execute("SELECT COUNT(*) FROM Customer")
        customer_count = database.c.fetchone()[0]
        database.c.execute("SELECT IFNULL(SUM(Fuel_Amount),0) FROM Invoice")
        total_fuel = database.c.fetchone()[0]

        # Display enhanced metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("إجمالي المبيعات", f"{total_sales:,.0f} ريال")
        with col2:
            st.metric("عدد العملاء", customer_count)
        with col3:
            st.metric("كمية الوقود المباعة", f"{total_fuel:,.0f} لتر")
        with col4:
            avg_sale = total_sales / max(customer_count, 1)
            st.metric("متوسط المبيعة للعميل", f"{avg_sale:.0f} ريال")

        # Quick actions
        st.subheader("⚡ الإجراءات السريعة")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📊 عرض التقارير", use_container_width=True):
                st.session_state.current_page = "reports"
                st.rerun()

        with col2:
            if st.button("⚙️ إدارة النظام", use_container_width=True):
                st.session_state.current_page = "management"
                st.rerun()

        with col3:
            if st.button("🧾 إنشاء فاتورة", use_container_width=True):
                st.session_state.current_page = "invoices"
                st.rerun()

        with col4:
            if st.button("⛽ إدارة الوقود", use_container_width=True):
                st.session_state.current_page = "fuel_management"
                st.rerun()

    elif "الإدارة" in section:
        # Enhanced management pages
        st.header("⚙️ الإدارة المحسنة")

        management_options = {
            "stations": "🏭 إدارة المحطات والمضخات والخزانات",
            "fuel_types": "⛽ إدارة أنواع الوقود",
            "employees": "👥 إدارة الموظفين",
            "invoices": "🧾 إدارة الفواتير",
            "supply": "🚛 إدارة توريد الوقود",
            "maintenance": "🔧 إدارة الصيانة"
        }

        if st.session_state.user_type in ["Admin", "Owner"]:
            selected_management = st.selectbox("اختر قسم الإدارة:", list(management_options.values()))
        else:
            # Filter based on permissions
            perms = st.session_state.permissions
            filtered_options = {}
            if "Management" in perms:
                filtered_options.update(management_options)
            else:
                if "Invoice" in perms:
                    filtered_options["invoices"] = management_options["invoices"]
                if "Supply" in perms:
                    filtered_options["supply"] = management_options["supply"]

            if not filtered_options:
                st.info("ليس لديك صلاحيات للوصول إلى أقسام الإدارة")
                st.stop()

            selected_management = st.selectbox("اختر قسم الإدارة:", list(filtered_options.values()))

        # Route to appropriate management page
        if selected_management == management_options["stations"]:
            management_stations()
        elif selected_management == management_options["fuel_types"]:
            management_fuel_types()
        elif selected_management == management_options["employees"]:
            management_employees()
        elif selected_management == management_options["invoices"]:
            management_invoices()
        elif selected_management == management_options["supply"]:
            management_supply()
        elif selected_management == management_options["maintenance"]:
            management_maintenance()

    elif "التقارير" in section:
        # Enhanced reports
        reports_enhanced()

def net_value():
    tanker_id = st.text_input("Enter Tanker ID:")
    result = TOTAL_Amount(tanker_id)
    if st.button("RUN Function"):
        df2 = pd.DataFrame(result, columns=["Total Amount"])
        st.dataframe(df2)

if __name__ == '__main__':
    main()
