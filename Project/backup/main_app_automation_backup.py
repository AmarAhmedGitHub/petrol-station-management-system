import streamlit as st
from pages.auth.login import main as auth_main
from pages.dashboard.main_dashboard import main as dashboard_main
from pages.management.main_management_enhanced import main as management_main
from pages.management.hardware_management import main as hardware_main
from pages.accounting.main_accounting import main as accounting_main
from pages.reports.main_reports_fixed import main as reports_main
from pages.sensor_monitoring import main as sensor_main

try:
    from pages.system_interface import main as system_main
except ImportError:
    system_main = None

from core.database_enhanced import create_enhanced_tables
from core.automation import start_scheduler
from core.sensor_api import initialize_sensor_api

def check_user_permissions(user_type, required_permission):
    """Check if user has required permission"""
    # Admin and Owner have access to ALL features
    if user_type in ['Admin', 'Owner']:
        return True

    # Employee permissions
    permissions = {
        'Employee': ['dashboard', 'management', 'reports', 'sensor_monitoring', 'accounting']
    }
    return required_permission in permissions.get(user_type, [])

def get_available_pages(user_type):
    """Get available pages based on user type"""
    all_pages = {
        'dashboard': ('📊 لوحة التحكم', 'dashboard'),
        'management': ('⚙️ الإدارة', 'management'),
        'hardware_management': ('🔧 إدارة الأجهزة والمعدات', 'hardware_management'),
        'accounting': ('💼 المحاسبة', 'accounting'),
        'reports': ('📈 التقارير', 'reports'),
        'sensor_monitoring': ('📡 مراقبة الاستشعار', 'sensor_monitoring'),
        'system_interface': ('🔧 واجهة النظام', 'system_interface')
    }

    if user_type == 'Admin':
        return all_pages
    elif user_type == 'Owner':
        return all_pages
    elif user_type == 'Employee':
        return {k: v for k, v in all_pages.items() if check_user_permissions(user_type, k)}
    else:
        return {'dashboard': all_pages['dashboard']}


def main():
    """Main application entry point"""
    # Set page configuration
    st.set_page_config(
        page_title="نظام إدارة محطات الوقود - مع الاستشعار الآلي والمحاسبة",
        page_icon="⛽",
        layout="wide",
        # initial_sidebar_state="dednaxpne"
    )
    
       
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'

    # Create database tables if they don't exist
    create_enhanced_tables()

    # Initialize sensor API and automation scheduler (only once)
    if 'automation_initialized' not in st.session_state:
        try:
            # Initialize sensor API with default demo configurations
            initialize_sensor_api()
            # Start the automated reconciliation scheduler
            scheduler = start_scheduler()
            st.session_state.scheduler = scheduler
            st.session_state.automation_initialized = True
            print("✅ Sensor API and automation scheduler initialized successfully")
        except Exception as e:
            print(f"⚠️ Warning: Failed to initialize automation: {str(e)}")
            st.session_state.automation_initialized = False

    # Use modern design system CSS
    from core.design_system import get_full_css
    from core.ui import render_sidebar_navigation
    st.markdown(f"<style>{get_full_css()}</style>", unsafe_allow_html=True)

    # Handle authentication first
    if not st.session_state.get('logged_in', False):
        # Clear sidebar to hide menu on login page
        st.sidebar.empty()

        # Add login mode class to body
        st.markdown('<div class="login-mode">', unsafe_allow_html=True)

        # Login page - show only header and login form
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        if auth_main():
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Footer for login page
        st.markdown("""
            <div class="footer">
                <p>© 2024 نظام إدارة محطات الوقود | جميع الحقوق محفوظة</p>
                <p>تم التطوير باستخدام Streamlit و MySQL</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Get user type and available pages
        user_type = st.session_state.get('user_type', 'Employee')
        available_pages = get_available_pages(user_type)

        # Main application after login
        # Main header
        st.markdown("""
            <div class="main-header">
                <h1>⛽ نظام إدارة محطات الوقود</h1>
                <p>نظام متكامل لإدارة محطات الوقود والمبيعات مع الاستشعار الآلي والمحاسبة</p>
            </div>
        """, unsafe_allow_html=True)

        # Show automation status
        if st.session_state.get('automation_initialized', False):
            st.markdown("""
                <div class="automation-status">
                    <span>🤖</span>
                    <span><strong>النظام الآلي:</strong> يعمل - التسوية التلقائية كل 7.5 ساعات</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ تحذير: النظام الآلي غير مفعل - سيتم استخدام القراءات المحاكاة فقط")

        # Sidebar navigation (centralized helper for consistent UX)
        selected_page = render_sidebar_navigation(available_pages,
                                                  st.session_state.current_page,
                                                  user_type,
                                                  st.session_state.get('username', ''))

        # If the helper returned a page, update state and rerun
        if selected_page and selected_page != st.session_state.current_page:
            st.session_state.current_page = selected_page
            st.rerun()

        # Main content area
        st.markdown('<div class="content-area">', unsafe_allow_html=True)

        # Render page header / breadcrumb
        from core.ui import render_page_header
        render_page_header(st.session_state.current_page, available_pages)

        # Check permissions before routing
        current_page = st.session_state.current_page
        if not check_user_permissions(user_type, current_page):
            st.error("❌ ليس لديك صلاحية للوصول لهذه الصفحة!")
            st.info("🔒 هذه الصفحة متاحة للمدراء والمالكين فقط.")
            st.session_state.current_page = 'dashboard'
            st.session_state['main_navigation'] = 'dashboard'
            current_page = 'dashboard'

        # Route to appropriate page based on current_page
        if current_page == 'dashboard':
            dashboard_main()
        elif current_page == 'management':
            management_main()
        elif current_page == 'hardware_management':
            hardware_main()
        elif current_page == 'accounting':
            accounting_main()
        elif current_page == 'reports':
            reports_main()
        elif current_page == 'sensor_monitoring':
            sensor_main()
        elif current_page == 'system_interface':
            if system_main:
                system_main()
            else:
                st.info("🚧 واجهة النظام غير متاحة حالياً")
        else:
            dashboard_main()  # Default to dashboard

        st.markdown('</div>', unsafe_allow_html=True)

        # Footer
        st.markdown("""
            <div class="footer">
                <p>© 2024 نظام إدارة محطات الوقود | جميع الحقوق محفوظة</p>
                <p>تم التطوير باستخدام Streamlit و MySQL مع الاستشعار الآلي والمحاسبة</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
