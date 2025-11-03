import streamlit as st
import pandas as pd
from core.database import get_connection

def check_admin_access():
    """Check if current user has admin access"""
    return (st.session_state.logged_in and
            st.session_state.user_type in ["Admin", "Owner"])

def show_admin_interface():
    """Display admin interface"""
    if not check_admin_access():
        st.error("❌ غير مسموح لك بالوصول لهذه الصفحة")
        return

    st.markdown("""
        <style>
        .admin-container {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
        }
        .admin-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .admin-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .admin-card:hover {
            transform: translateY(-5px);
            border-color: #dc3545;
            box-shadow: 0 8px 25px rgba(220,53,69,0.2);
        }
        .admin-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .admin-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #dc3545;
            margin-bottom: 1rem;
        }
        .admin-description {
            color: #6c757d;
            margin-bottom: 1.5rem;
        }
        .admin-button {
            background: linear-gradient(45deg, #dc3545, #c82333) !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 0.75rem 2rem !important;
            font-size: 1rem !important;
            font-weight: bold !important;
            width: 100% !important;
            margin-top: 1rem !important;
        }
        .section-header {
            color: #dc3545;
            font-size: 2rem;
            font-weight: bold;
            margin: 2rem 0 1rem 0;
            text-align: center;
        }
        .system-status {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin: 2rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="section-header">⚙️ إدارة النظام</h1>', unsafe_allow_html=True)

    # System Status
    st.markdown('<div class="system-status">', unsafe_allow_html=True)
    st.subheader("📊 حالة النظام")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👤 المستخدم الحالي", st.session_state.username)
    with col2:
        st.metric("🏷️ نوع المستخدم", st.session_state.user_type)
    with col3:
        st.metric("🔐 حالة الدخول", "نشط" if st.session_state.logged_in else "غير نشط")
    with col4:
        st.metric("⏰ وقت الدخول", "الآن")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="admin-grid">', unsafe_allow_html=True)

    # User Management
    st.markdown('''
        <div class="admin-card">
            <div class="admin-icon">👥</div>
            <div class="admin-title">إدارة المستخدمين</div>
            <div class="admin-description">
                إدارة حسابات المستخدمين وصلاحيات الوصول
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("👥 إدارة المستخدمين", key="user_mgmt", use_container_width=True):
        st.session_state.admin_page = "users"
        st.rerun()

    # System Settings
    st.markdown('''
        <div class="admin-card">
            <div class="admin-icon">⚙️</div>
            <div class="admin-title">إعدادات النظام</div>
            <div class="admin-description">
                إعدادات قاعدة البيانات والنظام العام
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("⚙️ إعدادات النظام", key="system_settings", use_container_width=True):
        st.session_state.admin_page = "settings"
        st.rerun()

    # Fuel Prices
    st.markdown('''
        <div class="admin-card">
            <div class="admin-icon">⛽</div>
            <div class="admin-title">إدارة أسعار الوقود</div>
            <div class="admin-description">
                تحديث أسعار الوقود وإدارة التسعير
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("⛽ إدارة أسعار الوقود", key="fuel_prices", use_container_width=True):
        st.session_state.admin_page = "fuel_prices"
        st.rerun()

    # Supply Management
    st.markdown('''
        <div class="admin-card">
            <div class="admin-icon">🚛</div>
            <div class="admin-title">إدارة التوريد</div>
            <div class="admin-description">
                إدارة توريد الوقود وتتبع الشحنات
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("🚛 إدارة التوريد", key="supply_mgmt", use_container_width=True):
        st.session_state.admin_page = "supply"
        st.rerun()

    # Database Management
    st.markdown('''
        <div class="admin-card">
            <div class="admin-icon">🗄️</div>
            <div class="admin-title">إدارة قاعدة البيانات</div>
            <div class="admin-description">
                نسخ احتياطي واستعادة قاعدة البيانات
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("🗄️ إدارة قاعدة البيانات", key="db_mgmt", use_container_width=True):
        st.session_state.admin_page = "database"
        st.rerun()

    # System Logs
    st.markdown('''
        <div class="admin-card">
            <div class="admin-icon">📋</div>
            <div class="admin-title">سجلات النظام</div>
            <div class="admin-description">
                عرض سجلات النظام والأنشطة
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("📋 سجلات النظام", key="system_logs", use_container_width=True):
        st.session_state.admin_page = "logs"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick Actions
    st.markdown('<h2 class="section-header">⚡ الإجراءات السريعة</h2>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 إعادة تشغيل النظام", key="restart_system", use_container_width=True):
            st.success("✅ تم إعادة تشغيل النظام بنجاح")

    with col2:
        if st.button("🧹 تنظيف البيانات المؤقتة", key="clear_cache", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ تم تنظيف البيانات المؤقتة")

    with col3:
        if st.button("📊 فحص صحة النظام", key="system_health", use_container_width=True):
            st.success("✅ النظام يعمل بشكل طبيعي")

def show_user_management():
    """Display user management interface"""
    st.markdown('<h2 class="section-header">👥 إدارة المستخدمين</h2>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📝 إضافة مستخدم", "📋 عرض المستخدمين", "⚙️ إدارة الصلاحيات"])

    with tab1:
        st.subheader("إضافة مستخدم جديد")
        with st.form("add_user"):
            col1, col2 = st.columns(2)

            with col1:
                user_type = st.selectbox("نوع المستخدم", ["Admin", "Owner", "Employee"])
                username = st.text_input("اسم المستخدم")
                password = st.text_input("كلمة المرور", type="password")

            with col2:
                email = st.text_input("البريد الإلكتروني")
                phone = st.text_input("رقم الهاتف")

            if st.form_submit_button("إضافة المستخدم", use_container_width=True):
                st.success("✅ تمت إضافة المستخدم بنجاح")

    with tab2:
        st.subheader("جميع المستخدمين")
        # Sample data - replace with actual database query
        users_data = [
            ["admin", "Admin", "نشط", "2024-01-01"],
            ["owner1", "Owner", "نشط", "2024-01-15"],
            ["emp001", "Employee", "نشط", "2024-02-01"]
        ]

        df = pd.DataFrame(users_data, columns=["اسم المستخدم", "نوع المستخدم", "الحالة", "تاريخ الإنشاء"])
        st.dataframe(df, use_container_width=True)

    with tab3:
        st.subheader("إدارة الصلاحيات")
        st.info("🚧 هذه الميزة قيد التطوير")

def show_system_settings():
    """Display system settings"""
    st.markdown('<h2 class="section-header">⚙️ إعدادات النظام</h2>', unsafe_allow_html=True)

    st.markdown('<div class="system-status">', unsafe_allow_html=True)
    st.subheader("إعدادات قاعدة البيانات")

    with st.form("db_settings"):
        col1, col2 = st.columns(2)

        with col1:
            db_host = st.text_input("خادم قاعدة البيانات", "localhost")
            db_name = st.text_input("اسم قاعدة البيانات", "Petrolpump_Management")
            db_user = st.text_input("اسم المستخدم", "root")

        with col2:
            db_port = st.number_input("منفذ قاعدة البيانات", value=3306)
            max_connections = st.number_input("الحد الأقصى للاتصالات", value=10)
            timeout = st.number_input("مهلة الاتصال (ثواني)", value=30)

        if st.form_submit_button("حفظ الإعدادات", use_container_width=True):
            st.success("✅ تم حفظ إعدادات قاعدة البيانات")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="system-status">', unsafe_allow_html=True)
    st.subheader("إعدادات النظام العام")

    with st.form("system_settings"):
        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input("اسم الشركة", "محطات الوقود")
            language = st.selectbox("اللغة", ["العربية", "English"])
            timezone = st.selectbox("المنطقة الزمنية", ["UTC", "Asia/Riyadh", "Africa/Cairo"])

        with col2:
            currency = st.selectbox("العملة", ["SAR", "USD", "EUR"])
            date_format = st.selectbox("تنسيق التاريخ", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
            theme = st.selectbox("المظهر", ["فاتح", "داكن", "تلقائي"])

        if st.form_submit_button("حفظ الإعدادات", use_container_width=True):
            st.success("✅ تم حفظ إعدادات النظام")

    st.markdown('</div>', unsafe_allow_html=True)

def show_fuel_prices():
    """Display fuel prices management"""
    st.markdown('<h2 class="section-header">⛽ إدارة أسعار الوقود</h2>', unsafe_allow_html=True)

    st.markdown('<div class="system-status">', unsafe_allow_html=True)
    st.subheader("أسعار الوقود الحالية")

    # Sample data - replace with actual database query
    fuel_prices = [
        ["بنزين 91", 2.18, "SAR"],
        ["بنزين 95", 2.33, "SAR"],
        ["ديزل", 2.15, "SAR"]
    ]

    df = pd.DataFrame(fuel_prices, columns=["نوع الوقود", "السعر", "العملة"])
    st.dataframe(df, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("تحديث أسعار الوقود")
    with st.form("update_fuel_prices"):
        col1, col2 = st.columns(2)

        with col1:
            fuel_type = st.selectbox("نوع الوقود", ["بنزين 91", "بنزين 95", "ديزل"])
            new_price = st.number_input("السعر الجديد", min_value=0.0, step=0.01)

        with col2:
            currency = st.selectbox("العملة", ["SAR", "USD", "EUR"])
            effective_date = st.date_input("تاريخ التفعيل")

        if st.form_submit_button("تحديث السعر", use_container_width=True):
            st.success(f"✅ تم تحديث سعر {fuel_type} إلى {new_price} {currency}")

def main():
    """Main admin function"""
    # Initialize session state
    if 'admin_page' not in st.session_state:
        st.session_state.admin_page = None

    # Navigation
    if st.session_state.admin_page is None:
        show_admin_interface()
    elif st.session_state.admin_page == "users":
        show_user_management()
        if st.button("⬅️ العودة للإدارة", key="back_to_admin"):
            st.session_state.admin_page = None
            st.rerun()
    elif st.session_state.admin_page == "settings":
        show_system_settings()
        if st.button("⬅️ العودة للإدارة", key="back_to_admin"):
            st.session_state.admin_page = None
            st.rerun()
    elif st.session_state.admin_page == "fuel_prices":
        show_fuel_prices()
        if st.button("⬅️ العودة للإدارة", key="back_to_admin"):
            st.session_state.admin_page = None
            st.rerun()

if __name__ == "__main__":
    main()
