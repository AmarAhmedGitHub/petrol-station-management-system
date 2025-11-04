"""
Centralized layout system for the PetrolPump Management System.
Provides consistent UI components and navigation patterns.
"""
import streamlit as st
from typing import Optional, Dict, List, Tuple

def render_page_header(title: str, description: str = None, icon: str = None):
    """
    Renders a consistent page header with optional description and icon.
    """
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        if icon:
            title = f":{icon}: {title}"
        st.markdown(f"## {title}")
        if description:
            st.markdown(f"<p style='color:#6c757d'>{description}</p>", unsafe_allow_html=True)
    with col2:
        st.write("")  # Spacing for potential actions/buttons

def render_section_nav(sections: List[Tuple[str, str]], active_section: str):
    """
    Renders section-based navigation with visual feedback for the active section.
    """
    st.markdown(
        """
        <style>
        .nav-section { 
            padding: 0.5rem 1rem;
            margin: 0.25rem;
            border-radius: 0.25rem;
            text-decoration: none;
            display: inline-block;
        }
        .nav-section.active {
            background-color: #0d6efd;
            color: white !important;
        }
        .nav-section:not(.active) {
            color: #0d6efd !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    nav_html = []
    for section_id, section_name in sections:
        active_class = "active" if section_id == active_section else ""
        nav_html.append(
            f'<a href="?section={section_id}" class="nav-section {active_class}">{section_name}</a>'
        )
    
    st.markdown("".join(nav_html), unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

def render_app_shell(page_title: str = None):
    """
    Renders the main application shell with consistent branding and layout.
    """
    if page_title:
        st.title(page_title)

def render_welcome_message(user_type: str, username: str):
    """
    Renders a contextual welcome message based on user type.
    """
    if user_type == "Admin":
        st.success("مرحباً بك، مسؤول النظام (Admin). لديك جميع الصلاحيات.")
    elif user_type == "Owner":
        st.success(f"مرحباً بك، المالك {username}. لديك جميع الصلاحيات.")
    elif user_type == "Employee":
        st.info(f"مرحباً بك، الموظف {username}. لديك صلاحيات محدودة حسب الإعدادات.")

def render_sidebar_menu(user_type: str, username: str):
    """
    Renders the main sidebar navigation menu with user context.
    """
    st.sidebar.image("https://img.icons8.com/color/96/000000/gas-pump.png", width=80)
    st.sidebar.markdown(f"<h2 style='color:#0d6efd;'>لوحة التحكم ({user_type})</h2>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<b>مرحباً، {username}!</b>", unsafe_allow_html=True)

    if st.sidebar.button("تسجيل الخروج", key="logout"):
        for k in ["logged_in", "user_type", "username", "show_emp_perms"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

def render_breadcrumbs(current_page: str, path: List[str] = None):
    """
    Renders a breadcrumb navigation showing the current page hierarchy.
    """
    if not path:
        path = ["الرئيسية", current_page]
    
    crumbs = " / ".join([f"<a href='#' style='color:#0d6efd;text-decoration:none'>{p}</a>" for p in path[:-1]])
    crumbs += f" / <span style='color:#6c757d'>{path[-1]}</span>"
    
    st.markdown(
        f"""
        <div style='margin-bottom:1rem'>
            {crumbs}
        </div>
        """,
        unsafe_allow_html=True
    )