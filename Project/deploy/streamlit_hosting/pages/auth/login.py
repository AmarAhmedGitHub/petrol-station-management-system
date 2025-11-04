import streamlit as st
import datetime
from core.auth_manager import get_auth_manager

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'permissions' not in st.session_state:
        st.session_state.permissions = []
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'locked_until' not in st.session_state:
        st.session_state.locked_until = None

def check_account_lock():
    """Check if account is locked due to multiple failed attempts"""
    now = datetime.datetime.now()
    if st.session_state.locked_until and now < st.session_state.locked_until:
        st.sidebar.error(f"تم قفل الحساب مؤقتاً بسبب تكرار المحاولات الخاطئة. الرجاء المحاولة بعد {st.session_state.locked_until.strftime('%H:%M:%S')}")
        return True
    return False

def handle_login(username, password):
    """Delegate login to AuthManager"""
    auth_mgr = get_auth_manager()
    success, msg = auth_mgr.handle_login(username, password)
    return success, msg

def show_login_page():
    """Display modern login page with professional design"""

    # Hide Streamlit header, menu, and sidebar
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stSidebar"] {display: none;}
        .main .block-container {max-width: none; padding-left: 0; padding-right: 0;}
        </style>
    """, unsafe_allow_html=True)

    # Login page container with modern design
    st.markdown("""
        <div class="login-page">
            <div class="login-container">
                <div class="login-header">
                    <div class="login-logo">⛽</div>
                    <h1 class="login-title">نظام إدارة محطات الوقود</h1>
                    <p class="login-subtitle">يرجى تسجيل الدخول للمتابعة</p>
                </div>
    """, unsafe_allow_html=True)

    # Login form
    with st.form("login_form", clear_on_submit=False):
        # Username field
        username = st.text_input(
            "👤 اسم المستخدم",
            placeholder="أدخل اسم المستخدم"
        )

        # Password field
        password = st.text_input(
            "🔒 كلمة المرور",
            type="password",
            placeholder="أدخل كلمة المرور"
        )

        # Submit button
        submitted = st.form_submit_button(
            "🚀 تسجيل الدخول",
            use_container_width=True
        )

    st.markdown("""
                <div class="login-footer">
                    <p>© 2024 نظام إدارة محطات الوقود | جميع الحقوق محفوظة</p>
                    <p>تم التطوير باستخدام Streamlit و MySQL</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Handle form submission
    if submitted:
        if not username or not password:
            st.markdown('<div class="login-alert error">⚠️ يرجى إدخال اسم المستخدم وكلمة المرور</div>', unsafe_allow_html=True)
        else:
            success, message = handle_login(username, password)
            if success:
                st.balloons()
                st.rerun()

def show_logout():
    """Display logout functionality"""
    if st.sidebar.button("🚪 تسجيل الخروج", key="logout", use_container_width=True):
        for key in ['logged_in', 'user_type', 'username', 'permissions', 'login_attempts', 'locked_until']:
            if key in st.session_state:
                del st.session_state[key]
        st.success("تم تسجيل الخروج بنجاح")
        st.rerun()

def show_user_info():
    """Display current user information"""
    if st.session_state.logged_in:
        # st.sidebar.markdown("---")
        st.sidebar.markdown(f"**👤 المستخدم:** {st.session_state.username}")
        st.sidebar.markdown(f"**🏷️ النوع:** {st.session_state.user_type}")

        # Display permissions for employees
        if st.session_state.user_type == "Employee" and st.session_state.permissions:
            st.sidebar.markdown("**🔑 الصلاحيات:**")
            for perm in st.session_state.permissions:
                st.sidebar.markdown(f"• {perm}")

def main():
    """Main authentication function"""
    init_session_state()

    # Check if user is already logged in
    if st.session_state.logged_in:
        show_user_info()
        show_logout()
        return True

    # Check if account is locked
    if check_account_lock():
        return False

    # Show login page
    show_login_page()
    return False

if __name__ == "__main__":
    main()
