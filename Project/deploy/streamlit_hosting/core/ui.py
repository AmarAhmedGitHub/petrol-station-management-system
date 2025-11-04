import streamlit as st
from typing import Dict, Tuple, Optional
from datetime import datetime
import time


def format_label(label_tuple: Tuple[str, str]) -> str:
    """Format the display label from pages mapping tuple like ('📊 لوحة التحكم', 'dashboard')"""
    return label_tuple[0]


def render_tab_navigation(available_pages: Dict[str, Tuple[str, str]],
                         current_page: str,
                         user_type: str,
                         username: str) -> Optional[str]:
    """Render an innovative tab-based navigation system and return the selected page id.

    - available_pages: mapping page_id -> (label, slug)
    - current_page: currently selected page id
    - user_type / username: used for user info display

    Returns the selected page id (or None if unchanged)
    """
    # Enhanced header with user info at the top
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="font-size: 2.5em;">⛽</div>
                <div>
                    <div style="font-weight: bold; font-size: 1.2em;">نظام إدارة محطات الوقود</div>
                    <div style="opacity: 0.9; font-size: 0.9em;">مرحباً بك، {username}</div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: bold; font-size: 1.1em;">{user_type}</div>
                <div style="opacity: 0.8; font-size: 0.8em;">{datetime.now().strftime('%H:%M:%S')}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Build nav options
    nav_items = list(available_pages.keys())

    if not nav_items:
        st.error("❌ لا توجد صفحات متاحة")
        return None

    # Ensure current_page is valid
    if current_page not in nav_items:
        current_page = nav_items[0]

    # Create tab labels with icons
    tab_labels = []
    for page_id in nav_items:
        label = available_pages[page_id][0]
        # Add icons based on page type
        icon_map = {
            'dashboard': '📊',
            'management': '⚙️',
            'hardware_management': '🔧',
            'shift_management': '🕐',
            'accounting': '💼',
            'reports': '📈',
            'sensor_monitoring': '📡',
            'system_interface': '🔧'
        }
        icon = icon_map.get(page_id, '📄')
        tab_labels.append(f"{icon} {label}")

    # Create tabs
    tabs = st.tabs(tab_labels)

    # Handle tab selection
    selected_page = None
    for i, (tab, page_id) in enumerate(zip(tabs, nav_items)):
        with tab:
            if page_id == current_page:
                # Current tab content
                st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
                        padding: 20px;
                        border-radius: 10px;
                        border-left: 4px solid #2196f3;
                        margin-bottom: 20px;
                    ">
                        <h3 style="margin: 0; color: #1976d2;">الصفحة الحالية</h3>
                        <p style="margin: 5px 0 0 0; color: #424242;">أنت الآن في هذه الصفحة</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Other tabs - show preview/navigation
                if st.button(f"🏃‍♂️ انتقل إلى {available_pages[page_id][0]}",
                           key=f"tab_nav_{page_id}",
                           use_container_width=True,
                           help=f"الانتقال إلى صفحة {available_pages[page_id][0]}"):
                    selected_page = page_id

                # Quick preview for each tab
                preview_content = get_page_preview(page_id)
                if preview_content:
                    st.markdown(preview_content)

    # Quick actions bar below tabs
    st.markdown("---")
    show_quick_actions_bar(user_type)

    return selected_page


def get_page_preview(page_id: str) -> str:
    """Get preview content for each page tab"""
    previews = {
        'dashboard': """
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4 style="margin: 0 0 10px 0; color: #495057;">📊 معاينة لوحة التحكم</h4>
                <p style="margin: 0; font-size: 0.9em; color: #6c757d;">
                    مراقبة شاملة لأداء المحطة مع مخططات تفاعلية ومؤشرات حية
                </p>
            </div>
        """,
        'management': """
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4 style="margin: 0 0 10px 0; color: #495057;">⚙️ معاينة الإدارة</h4>
                <p style="margin: 0; font-size: 0.9em; color: #6c757d;">
                    إدارة المحطات والموظفين والعمليات اليومية
                </p>
            </div>
        """,
        'shift_management': """
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4 style="margin: 0 0 10px 0; color: #495057;">🕐 معاينة إدارة المناوبات</h4>
                <p style="margin: 0; font-size: 0.9em; color: #6c757d;">
                    إدارة فترات الدوام والمناوبات مع جدولة ذكية
                </p>
            </div>
        """,
        'accounting': """
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4 style="margin: 0 0 10px 0; color: #495057;">💼 معاينة المحاسبة</h4>
                <p style="margin: 0; font-size: 0.9em; color: #6c757d;">
                    نظام محاسبي متكامل مع الفواتير والتقارير المالية
                </p>
            </div>
        """,
        'reports': """
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4 style="margin: 0 0 10px 0; color: #495057;">📈 معاينة التقارير</h4>
                <p style="margin: 0; font-size: 0.9em; color: #6c757d;">
                    تحليلات متقدمة وتقارير مفصلة لجميع العمليات
                </p>
            </div>
        """
    }

    return previews.get(page_id, "")


def show_quick_actions_bar(user_type: str):
    """Show quick actions bar below tabs"""
    st.markdown("### ⚡ إجراءات سريعة")

    # Create action buttons in columns
    actions = [
        {"icon": "🔍", "label": "بحث", "action": "search", "color": "#2563eb"},
        {"icon": "📊", "label": "إحصائيات", "action": "stats", "color": "#059669"},
        {"icon": "⚙️", "label": "إعدادات", "action": "settings", "color": "#ea580c"},
        {"icon": "🚪", "label": "خروج", "action": "logout", "color": "#dc2626"}
    ]

    cols = st.columns(len(actions))

    for i, action in enumerate(actions):
        with cols[i]:
            if st.button(
                f"{action['icon']} {action['label']}",
                key=f"quick_{action['action']}",
                use_container_width=True,
                help=f"الوصول السريع لـ {action['label']}"
            ):
                handle_quick_action(action['action'])

    # Permission notice for employees
    if user_type == 'Employee':
        st.markdown("""
            <div style="
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 12px;
                margin: 15px 0;
                font-size: 0.9em;
                text-align: center;
            ">
                <strong>ℹ️ تنبيه:</strong> بعض الواجهات متاحة للمالكين والمديرين فقط
            </div>
        """, unsafe_allow_html=True)


def handle_quick_action(action: str):
    """Handle quick action button clicks"""
    if action == "search":
        st.info("🔍 البحث - سيتم تطوير هذا القسم قريباً")
    elif action == "stats":
        try:
            from core.database_enhanced import get_dashboard_stats
            stats = get_dashboard_stats()
            if stats:
                st.markdown("#### 📊 إحصائيات سريعة")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("المحطات", stats.get('total_stations', 0))
                with col2:
                    st.metric("المضخات", stats.get('total_pumps', 0))
                with col3:
                    st.metric("الموظفين", stats.get('total_employees', 0))
                with col4:
                    st.metric("الخزانات", stats.get('total_tanks', 0))
        except Exception as e:
            st.error(f"خطأ في جلب الإحصائيات: {e}")
    elif action == "settings":
        st.info("⚙️ الإعدادات - سيتم تطوير هذا القسم قريباً")
    elif action == "logout":
        # Clear session state safely
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        # Trigger a rerun so the app returns to login
        st.rerun()


# Backward compatibility - alias for the new function
def render_sidebar_navigation(available_pages: Dict[str, Tuple[str, str]],
                              current_page: str,
                              user_type: str,
                              username: str) -> Optional[str]:
    """Backward compatibility alias for tab navigation"""
    return render_tab_navigation(available_pages, current_page, user_type, username)


def render_page_header(page_id: str, available_pages: Dict[str, Tuple[str, str]]):
    """Render an innovative page header with enhanced navigation and context.

    - page_id: current page key
    - available_pages: mapping page_id -> (label, slug)
    """
    # Ensure navigation history exists in session_state
    if 'nav_history' not in st.session_state:
        st.session_state['nav_history'] = []

    # Append to history only if last item differs
    if not st.session_state['nav_history'] or st.session_state['nav_history'][-1] != page_id:
        st.session_state['nav_history'].append(page_id)

    title = available_pages.get(page_id, (page_id, ""))[0]

    # Enhanced description mapping with more context
    descriptions = {
        'dashboard': 'مراقبة شاملة لأداء المحطة والمؤشرات الرئيسية والتحليلات اليومية',
        'management': 'إدارة شاملة للمحطات، الموظفين، الفواتير والعمليات اليومية',
        'hardware_management': 'لوحة متقدمة لإدارة الأجهزة، المضخات، الخزانات والصيانة',
        'accounting': 'نظام محاسبي متكامل مع الفواتير، السجلات المالية والتقارير',
        'reports': 'تحليلات متقدمة وتقارير تفصيلية لجميع جوانب العمليات',
        'sensor_monitoring': 'مراقبة مباشرة لبيانات الحساسات وقراءات الوقود والأداء',
        'system_interface': 'واجهة النظام المتقدمة والإعدادات والتكوينات',
        'login': 'نقطة الدخول الآمنة للنظام مع التحقق من الهوية'
    }

    desc = descriptions.get(page_id, 'صفحة النظام')

    # Enhanced breadcrumb with modern design - إخفاء مسار التنقل لتجنب التكرار
    # history = st.session_state.get('nav_history', [])
    # if len(history) > 1:  # Only show breadcrumb if there's navigation history
    #     st.markdown("""
    #         <div style="
    #             background: #f8f9fa;
    #             border-radius: 10px;
    #             padding: 10px 15px;
    #             margin-bottom: 20px;
    #             border-left: 4px solid #007bff;
    #         ">
    #     """, unsafe_allow_html=True)
    #
    #     st.markdown("**🧭 مسار التنقل:**")
    #
    #     # Create breadcrumb trail
    #     breadcrumb_items = []
    #     for i, pid in enumerate(history):
    #         label = available_pages.get(pid, (pid, ''))[0]
    #         if i < len(history) - 1:
    #             # Clickable breadcrumb for navigation history
    #             if st.button(f"📍 {label}", key=f"bc_{pid}_{i}_{page_id}", help=f"العودة إلى {label}"):
    #                 st.session_state['nav_history'] = history[: i + 1]
    #                 st.session_state['current_page'] = pid
    #                 st.rerun()
    #         else:
    #             # Current page (highlighted)
    #             st.markdown(f"**🏠 {label}** ← الصفحة الحالية")
    #
    #     st.markdown("</div>", unsafe_allow_html=True)

    # Enhanced page header with modern design and context
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px 30px;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px rgba(102,126,234,0.3);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -50px;
                right: -50px;
                width: 150px;
                height: 150px;
                background: rgba(255,255,255,0.1);
                border-radius: 50%;
            "></div>
            <div style="
                position: absolute;
                bottom: -30px;
                left: -30px;
                width: 100px;
                height: 100px;
                background: rgba(255,255,255,0.05);
                border-radius: 50%;
            "></div>
            <div style="position: relative; z-index: 1;">
                <h1 style="
                    margin: 0 0 10px 0;
                    font-size: 2.2em;
                    font-weight: 700;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    display: flex;
                    align-items: center;
                    gap: 15px;
                ">
                    {title}
                    <span style="font-size: 0.6em; opacity: 0.8; background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 20px;">{page_id.upper()}</span>
                </h1>
                <p style="
                    margin: 0;
                    font-size: 1.1em;
                    opacity: 0.9;
                    font-weight: 300;
                    line-height: 1.5;
                ">{desc}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Add contextual quick actions based on current page
    quick_actions = get_page_quick_actions(page_id)
    if quick_actions:
        st.markdown("### ⚡ إجراءات سريعة")
        cols = st.columns(len(quick_actions))
        for i, action in enumerate(quick_actions):
            with cols[i]:
                if st.button(action['label'], key=f"quick_{page_id}_{i}", use_container_width=True):
                    if action.get('action'):
                        action['action']()
                    else:
                        st.info(f"سيتم تنفيذ: {action['label']}")


def get_page_quick_actions(page_id: str) -> list:
    """Get contextual quick actions for the current page"""
    actions_map = {
        'dashboard': [
            {'label': '📊 تحديث البيانات', 'action': lambda: st.rerun()},
            {'label': '📈 عرض التقارير', 'action': None},
            {'label': '⚙️ إعدادات التنبيهات', 'action': None}
        ],
        'management': [
            {'label': '➕ إضافة محطة', 'action': None},
            {'label': '👥 إدارة الموظفين', 'action': None},
            {'label': '📋 التقارير', 'action': None}
        ],
        'shift_management': [
            {'label': '🆕 مناوبة جديدة', 'action': None},
            {'label': '👥 تعيين الموظفين', 'action': None},
            {'label': '📅 عرض الجدولة', 'action': None}
        ],
        'accounting': [
            {'label': '💰 فاتورة جديدة', 'action': None},
            {'label': '📊 الحسابات', 'action': None},
            {'label': '📈 التقارير المالية', 'action': None}
        ],
        'reports': [
            {'label': '📊 تقرير المبيعات', 'action': None},
            {'label': '📈 التحليلات', 'action': None},
            {'label': '📥 تصدير البيانات', 'action': None}
        ]
    }

    return actions_map.get(page_id, [])

