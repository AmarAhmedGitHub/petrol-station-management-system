"""
نظام إدارة محطات الوقود - التطبيق الرئيسي الموحد
Fuel Station Management System - Unified Main Application

هذا الملف يحتوي على التطبيق الرئيسي الموحد والمنظم لنظام إدارة محطات الوقود.
"""

import streamlit as st
from pages.auth.login import main as auth_main
from core.database_enhanced import create_enhanced_tables
from core.automation import start_scheduler
from core.sensor_api import initialize_sensor_api
from core.design_system import get_full_css
from core.ui import render_sidebar_navigation, render_page_header
from core.app_config import get_page_config
from core.auth_manager import get_auth_manager
from core.page_router import get_page_router
from core.safe_html import get_safe_html


def initialize_application():
    """Initialize application components"""
    # Set page configuration
    page_config = get_page_config()
    st.set_page_config(**page_config)

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

    # Apply design system CSS
    st.markdown(f"<style>{get_full_css()}</style>", unsafe_allow_html=True)


def render_login_page():
    """Render the login page"""
    # Hide sidebar completely on login page
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }Project/main_app.py
            .main {
                margin-left: 0 !important;
                padding-left: 0 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Login page container
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


def render_main_application():
    """Render the main application after login"""
    auth_mgr = get_auth_manager()
    page_router = get_page_router()
    safe_html = get_safe_html()

    # Get user type and available pages
    user_info = auth_mgr.get_current_user_info()
    user_type = user_info['user_type']
    available_pages = page_router.get_available_pages(user_type)

    # Main header - استخدام HTML آمن
    safe_html.display_main_header(
        "نظام إدارة محطات الوقود",
        "نظام متكامل لإدارة محطات الوقود والمبيعات مع الاستشعار الآلي والمحاسبة"
    )

    # Show automation status - استخدام HTML آمن
    safe_html.display_automation_status(
        st.session_state.get('automation_initialized', False)
    )

    # Hide sidebar completely in main application - convert to tabs navigation
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            .main {
                margin-left: 0 !important;
                padding-left: 0 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Create tabs navigation instead of sidebar
    tab_names = []
    tab_functions = []

    for page_key, (page_name, page_icon) in available_pages.items():
        tab_names.append(f"{page_icon} {page_name}")
        tab_functions.append(page_key)

    # Create tabs and handle navigation
    if tab_names:
        tabs = st.tabs(tab_names)

        # Render content for each tab
        for i, (tab, page_key) in enumerate(zip(tabs, tab_functions)):
            with tab:
                # Update current page when tab is active
                st.session_state.current_page = page_key

                # Check permissions before rendering
                if not auth_mgr.check_permission(user_type, page_key):
                    st.error("❌ ليس لديك صلاحية للوصول لهذه الصفحة!")
                    st.info("🔒 هذه الصفحة متاحة للمدراء والمالكين فقط.")
                    continue

                # Render page header for this tab
                render_page_header(page_key, available_pages)

                # Route to appropriate page
                page_router.route_to_page(page_key)
    else:
        st.error("لا توجد صفحات متاحة للمستخدم الحالي")
        return






def main():
    """Main application entry point"""
    initialize_application()

    # Handle authentication
    if not st.session_state.get('logged_in', False):
        render_login_page()
    else:
        render_main_application()


if __name__ == "__main__":
    main()
