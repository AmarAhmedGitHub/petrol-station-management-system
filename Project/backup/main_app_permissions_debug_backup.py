import streamlit as st
import logging
from pages.auth.login import main as auth_main
from pages.dashboard.main_dashboard import main as dashboard_main
from pages.management.main_management_fixed import main as management_main
from pages.reports.main_reports_fixed import main as reports_main
from pages.admin.main_admin import main as admin_main
from core.database import create_tables

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_user_permissions(user_type, required_permission):
    """Check if user has required permission"""
    logger.debug(f"User type = {user_type}, Required permission = {required_permission}")

    permissions = {
        'Admin': ['dashboard', 'management', 'reports', 'admin'],
        'Owner': ['dashboard', 'management', 'reports', 'admin'],
        'Employee': ['dashboard', 'management', 'reports']
    }

    user_permissions = permissions.get(user_type, [])
    result = required_permission in user_permissions

    logger.debug(f"User permissions = {user_permissions}, Result = {result}")
    return result

def get_available_pages(user_type):
    """Get available pages based on user type"""
    logger.debug(f"Getting available pages for user type = {user_type}")

    all_pages = {
        'dashboard': ('📊 لوحة التحكم', 'dashboard'),
        'management': ('⚙️ الإدارة', 'management'),
        'reports': ('📈 التقارير', 'reports'),
        'admin': ('🔧 الإدارة المتقدمة', 'admin')
    }

    if user_type == 'Admin':
        logger.debug("Admin user - returning all pages")
        return all_pages
    elif user_type == 'Owner':
        logger.debug("Owner user - returning all pages")
        return all_pages
    elif user_type == 'Employee':
        logger.debug("Employee user - returning limited pages")
        return {k: v for k, v in all_pages.items() if k != 'admin'}
    else:
        logger.debug("Unknown user type - returning dashboard only")
        return {'dashboard': all_pages['dashboard']}

def main():
    """Main application entry point"""
    # Set page configuration
    st.set_page_config(
        page_title="نظام إدارة محطات الوقود",
        page_icon="⛽",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'

    # Create database tables if they don't exist
    create_tables()

    # Custom CSS for the entire application
    st.markdown("""
        <style>
        /* Global styles */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .main-header h1 {
            font-size: 3rem;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .main-header p {
            font-size: 1.3rem;
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }

        /* Login page styles */
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .login-header h1 {
            font-size: 3rem;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .login-header p {
            font-size: 1.3rem;
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        .login-container {
            background: white;
            padding: 3rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: 0 auto;
        }

        /* Sidebar styles */
        .sidebar-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sidebar-header h2 {
            font-size: 1.5rem;
            margin: 0;
        }

        /* Navigation buttons */
        .nav-button {
            background: linear-gradient(45deg, #667eea, #764ba2) !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 0.75rem 1.5rem !important;
            font-size: 1rem !important;
            font-weight: bold !important;
            width: 100% !important;
            margin: 0.5rem 0 !important;
            transition: all 0.3s ease !important;
            color: white !important;
        }
        .nav-button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 15px rgba(102,126,234,0.4) !important;
        }

        /* Active page indicator */
        .nav-button.active {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24) !important;
            box-shadow: 0 5px 15px rgba(255,107,107,0.4) !important;
        }

        /* Disabled button */
        .nav-button.disabled {
            background: #cccccc !important;
            color: #666666 !important;
            cursor: not-allowed !important;
        }

        /* Content area */
        .content-area {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            min-height: 600px;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: #6c757d;
            font-size: 0.9rem;
            margin-top: 2rem;
            border-top: 1px solid #dee2e6;
        }

        /* Permission warning */
        .permission-warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            color: #856404;
        }

        /* Debug info */
        .debug-info {
            background: #e7f3ff;
            border: 1px solid #b3d4fc;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            color: #084c7e;
            font-size: 0.8rem;
        }

        /* Hide default streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}

        /* Hide sidebar only when not logged in */
        .login-mode [data-testid="stSidebar"] {
            display: none !important;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .main-header h1, .login-header h1 {
                font-size: 2rem;
            }
            .main-header p, .login-header p {
                font-size: 1rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # Handle authentication first
    if not st.session_state.get('logged_in', False):
        # Add login mode class to body
        st.markdown('<div class="login-mode">', unsafe_allow_html=True)

        # Login page - show only header and login form
        st.markdown("""
            <div class="login-header">
                <h1>⛽ نظام إدارة محطات الوقود</h1>
                <p>يرجى تسجيل الدخول للوصول إلى النظام</p>
            </div>
        """, unsafe_allow_html=True)

        # Login form
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

        # Debug information
        st.markdown(f"""
            <div class="debug-info">
                <strong>🐛 معلومات التصحيح:</strong><br>
                • نوع المستخدم: {user_type}<br>
                • الصفحات المتاحة: {list(available_pages.keys())}<br>
                • الصفحة الحالية: {st.session_state.current_page}
            </div>
        """, unsafe_allow_html=True)

        # Main application after login
        # Main header
        st.markdown("""
            <div class="main-header">
                <h1>⛽ نظام إدارة محطات الوقود</h1>
                <p>نظام متكامل لإدارة محطات الوقود والمبيعات</p>
            </div>
        """, unsafe_allow_html=True)

        # Sidebar navigation
        with st.sidebar:
            st.markdown("""
                <div class="sidebar-header">
                    <h2>🗂️ القائمة الرئيسية</h2>
                </div>
            """, unsafe_allow_html=True)

            # Navigation buttons based on permissions
            for page_id, (label, page_name) in available_pages.items():
                button_class = "nav-button active" if st.session_state.current_page == page_id else "nav-button"
                if st.button(label, key=f"nav_{page_id}", use_container_width=True):
                    st.session_state.current_page = page_id
                    st.rerun()

            # Show permission info for admin page if user is employee
            if user_type == 'Employee':
                st.markdown("""
                    <div class="permission-warning">
                        <strong>ℹ️ تنبيه:</strong><br>
                        الإدارة المتقدمة متاحة للمدراء والمالكين فقط
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # User info and logout
            st.write(f"**👤 المستخدم:** {st.session_state.get('username', '')}")
            st.write(f"**🏷️ النوع:** {st.session_state.get('user_type', '')}")

            # Show permissions info
            if user_type == 'Admin':
                st.write("**🔑 الصلاحيات:** جميع الصلاحيات")
            elif user_type == 'Owner':
                st.write("**🔑 الصلاحيات:** مالك - جميع الصلاحيات")
            elif user_type == 'Employee':
                st.write("**🔑 الصلاحيات:** موظف - محدودة")

            if st.button("🚪 تسجيل الخروج", key="logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        # Main content area
        st.markdown('<div class="content-area">', unsafe_allow_html=True)

        # Check permissions before routing
        current_page = st.session_state.current_page
        if not check_user_permissions(user_type, current_page):
            st.error("❌ ليس لديك صلاحية للوصول لهذه الصفحة!")
            st.info("🔒 هذه الصفحة متاحة للمدراء والمالكين فقط.")
            st.session_state.current_page = 'dashboard'
            current_page = 'dashboard'

        # Route to appropriate page based on current_page
        if current_page == 'dashboard':
            dashboard_main()
        elif current_page == 'management':
            management_main()
        elif current_page == 'reports':
            reports_main()
        elif current_page == 'admin':
            admin_main()
        else:
            dashboard_main()  # Default to dashboard

        st.markdown('</div>', unsafe_allow_html=True)

        # Footer
        st.markdown("""
            <div class="footer">
                <p>© 2024 نظام إدارة محطات الوقود | جميع الحقوق محفوظة</p>
                <p>تم التطوير باستخدام Streamlit و MySQL</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
