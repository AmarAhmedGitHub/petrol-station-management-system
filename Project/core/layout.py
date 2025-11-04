import streamlit as st
from typing import Optional
from .design_system import get_full_css
from .page_router import get_page_router


def apply_global_css(theme: str = 'light') -> None:
    """Inject the global design CSS into the Streamlit page."""
    css = get_full_css(theme=theme, rtl=True)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_header(title: str = "نظام إدارة محطات الوقود", subtitle: Optional[str] = None) -> None:
    """Render a consistent header using the design system."""
    st.markdown(f"<div class=\"main-header\"><h1>{title}</h1>\n")
    if subtitle:
        st.markdown(f"<p>{subtitle}</p>")
    st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar_menu(user_type: str) -> str:
    """Render the sidebar menu and return the selected page id.

    Uses the central PageRouter to get available pages for the user and
    displays them as a radio-style navigation in the sidebar.
    """
    pr = get_page_router()
    available = pr.get_available_pages(user_type)

    # available is expected to be a dict: {page_id: (label, icon)}
    labels = []
    keys = []
    for pid, meta in available.items():
        if isinstance(meta, (list, tuple)) and len(meta) >= 1:
            label = meta[0]
        else:
            label = pid
        labels.append(label)
        keys.append(pid)

    # Use radio to show navigation (nice keyboard + ARIA support)
    if 'current_page' not in st.session_state:
        st.session_state.current_page = pr.get_default_page(user_type)

    choice_label = st.sidebar.radio("القائمة الرئـيسية", labels, index=labels.index(available.get(st.session_state.current_page, (labels[0],))[0]) if labels else 0)

    # map back to page id
    try:
        sel_index = labels.index(choice_label)
        sel_page = keys[sel_index]
    except Exception:
        sel_page = st.session_state.current_page

    st.session_state.current_page = sel_page

    # Logout control
    if st.sidebar.button("تسجيل الخروج", key="layout_logout"):
        for k in ["logged_in", "user_type", "username", "permissions", 'current_page', 'login_attempts', 'locked_until']:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    return sel_page


def render_content_for_page(page_id: str) -> None:
    """Delegate rendering to PageRouter for the given page id."""
    pr = get_page_router()
    # Validate access
    user_type = st.session_state.get('user_type', 'Employee')
    if not pr.validate_page_access(user_type, page_id):
        st.warning("لا تملك الصلاحية للوصول إلى هذه الصفحة.")
        page_id = pr.get_default_page(user_type)

    pr.route_to_page(page_id)


def render_app_shell(user_type: str, title: str = "نظام إدارة محطات الوقود") -> None:
    """Convenience helper to render full shell: CSS, header, sidebar and current page content."""
    apply_global_css(theme='light')
    render_header(title)
    sel = render_sidebar_menu(user_type)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    render_content_for_page(sel)
    st.markdown('</div>', unsafe_allow_html=True)
