"""
Management Orchestrator - Main Management Interface Coordinator

This module coordinates all management interfaces and provides the main navigation
structure for settings, addition, and reports interfaces.
"""

import streamlit as st
from .settings_manager import SettingsManager
from .addition_manager import AdditionManager
from .reports_manager import ReportsManager


class ManagementOrchestrator:
    """Main orchestrator for all management interfaces"""

    def __init__(self):
        """Initialize the orchestrator with all managers"""
        self.settings_manager = SettingsManager()
        self.addition_manager = AdditionManager()
        self.reports_manager = ReportsManager()

    def show_main_interface(self):
        """Display the main management interface with organized navigation"""
        st.markdown("""
            <style>
            .management-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin: 1rem 0;
                text-align: center;
            }
            .category-card {
                background: white;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin: 1rem 0;
                border-left: 5px solid #667eea;
                transition: transform 0.3s ease;
            }
            .category-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0,0,0,0.2);
            }
            .nav-button {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
                width: 100%;
                margin: 0.5rem 0;
                transition: all 0.3s ease;
            }
            .nav-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102,126,234,0.4);
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin: 1rem 0;
            }
            .stat-card {
                background: white;
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)

        # Main header
        st.markdown('<h1 class="management-header">⚙️ نظام إدارة محطات الوقود المحسن</h1>', unsafe_allow_html=True)

        # Initialize session state
        if 'management_section' not in st.session_state:
            st.session_state.management_section = None

        # Navigation logic
        if st.session_state.management_section is None:
            self._show_main_navigation()
        elif st.session_state.management_section == 'settings':
            self.settings_manager.show_settings_interface()
            if st.button("⬅️ العودة للقائمة الرئيسية", key="back_to_main"):
                st.session_state.management_section = None
                st.rerun()
        elif st.session_state.management_section == 'addition':
            self.addition_manager.show_addition_interface()
            if st.button("⬅️ العودة للقائمة الرئيسية", key="back_to_main"):
                st.session_state.management_section = None
                st.rerun()
        elif st.session_state.management_section == 'reports':
            self.reports_manager.show_reports_interface()
            if st.button("⬅️ العودة للقائمة الرئيسية", key="back_to_main"):
                st.session_state.management_section = None
                st.rerun()

    def _show_main_navigation(self):
        """Display the main navigation with three main categories"""
        st.markdown("""
            <div style="text-align: center; margin: 2rem 0;">
                <h3 style="color: #667eea; margin-bottom: 2rem;">اختر الفئة المطلوبة</h3>
            </div>
        """, unsafe_allow_html=True)

        # Create three main category cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
                <div class="category-card">
                    <h4 style="color: #667eea; margin-bottom: 1rem;">⚙️ الإعدادات والتكوين</h4>
                    <p style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">
                        إدارة إعدادات النظام، أنواع الوقود، المناوبات، والتكوينات الأساسية
                    </p>
                </div>
            """, unsafe_allow_html=True)

            if st.button("📋 الإعدادات والتكوين", key="settings_btn", use_container_width=True):
                st.session_state.management_section = 'settings'
                st.rerun()

        with col2:
            st.markdown("""
                <div class="category-card">
                    <h4 style="color: #667eea; margin-bottom: 1rem;">➕ الإضافة والإدارة</h4>
                    <p style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">
                        إضافة وإدارة المحطات، الموظفين، المضخات، الخزانات، والعمليات الأساسية
                    </p>
                </div>
            """, unsafe_allow_html=True)

            if st.button("🛠️ الإضافة والإدارة", key="addition_btn", use_container_width=True):
                st.session_state.management_section = 'addition'
                st.rerun()

        with col3:
            st.markdown("""
                <div class="category-card">
                    <h4 style="color: #667eea; margin-bottom: 1rem;">📊 التقارير والتحليلات</h4>
                    <p style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">
                        عرض التقارير، الإحصائيات، والتحليلات لجميع العمليات والأداء
                    </p>
                </div>
            """, unsafe_allow_html=True)

            if st.button("📈 التقارير والتحليلات", key="reports_btn", use_container_width=True):
                st.session_state.management_section = 'reports'
                st.rerun()

        # Quick statistics overview
        st.markdown("---")
        st.markdown('<h3 style="color: #667eea; text-align: center; margin: 2rem 0 1rem 0;">📈 نظرة سريعة على النظام</h3>', unsafe_allow_html=True)

        # Get quick stats
        stats = self._get_quick_stats()

        # Display stats in a grid
        st.markdown('<div class="stats-grid">', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("إجمالي المحطات", stats.get('stations', 0))

        with col2:
            st.metric("إجمالي الموظفين", stats.get('employees', 0))

        with col3:
            st.metric("إجمالي المضخات", stats.get('pumps', 0))

        with col4:
            st.metric("إجمالي الخزانات", stats.get('tanks', 0))

        st.markdown('</div>', unsafe_allow_html=True)

        # Additional quick actions
        st.markdown("---")
        st.markdown('<h4 style="color: #667eea; text-align: center; margin: 1rem 0;">⚡ الإجراءات السريعة</h4>', unsafe_allow_html=True)

        quick_col1, quick_col2, quick_col3 = st.columns(3)

        with quick_col1:
            if st.button("🔗 إدارة التعيينات", key="quick_assignments", use_container_width=True):
                st.session_state.management_section = 'addition'
                st.session_state.addition_subsection = 'assignments'
                st.rerun()

        with quick_col2:
            if st.button("📊 لوحة المراقبة", key="quick_dashboard", use_container_width=True):
                st.session_state.page = 'dashboard'
                st.rerun()

        with quick_col3:
            if st.button("🔍 البحث المتقدم", key="quick_search", use_container_width=True):
                st.session_state.management_section = 'reports'
                st.session_state.reports_subsection = 'search'
                st.rerun()

    def _get_quick_stats(self):
        """Get quick statistics for the overview"""
        try:
            from core.database_enhanced import (
                get_all_stations, get_all_employees,
                get_all_pumps, get_all_tanks
            )

            return {
                'stations': len(get_all_stations() or []),
                'employees': len(get_all_employees() or []),
                'pumps': len(get_all_pumps() or []),
                'tanks': len(get_all_tanks() or [])
            }
        except Exception as e:
            st.error(f"خطأ في استرجاع الإحصائيات: {e}")
            return {'stations': 0, 'employees': 0, 'pumps': 0, 'tanks': 0}


def main():
    """Main function for the management orchestrator"""
    if not st.session_state.get('logged_in', False):
        st.warning("⚠️ يجب تسجيل الدخول للوصول إلى صفحة الإدارة.")
        return

    orchestrator = ManagementOrchestrator()
    orchestrator.show_main_interface()


if __name__ == "__main__":
    main()
