"""
Reports Manager - Analytics and Reporting Interfaces

This module handles all reporting and analytics interfaces for the system.
"""

import streamlit as st
import pandas as pd
from core.database_enhanced import (
    get_all_stations, get_all_pumps, get_all_tanks, get_all_employees,
    get_all_fuel_types, get_all_invoices, get_all_supplies
)


class ReportsManager:
    """Manager for all reports and analytics interfaces"""

    def __init__(self):
        """Initialize the reports manager"""
        pass

    def show_reports_interface(self):
        """Display the main reports interface"""
        st.markdown("""
            <style>
            .reports-header {
                background: linear-gradient(135deg, #fd7e14 0%, #e8680d 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin: 1rem 0;
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<h1 class="reports-header">📊 التقارير والتحليلات</h1>', unsafe_allow_html=True)

        # Navigation tabs for different report categories
        reports_tabs = st.tabs([
            "📈 التقارير العامة",
            "⛽ تقارير المبيعات",
            "🏭 تقارير المحطات",
            "👥 تقارير الموظفين",
            "🔧 تقارير الصيانة",
            "📊 التحليلات المتقدمة"
        ])

        with reports_tabs[0]:
            self._general_reports()

        with reports_tabs[1]:
            self._sales_reports()

        with reports_tabs[2]:
            self._stations_reports()

        with reports_tabs[3]:
            self._employees_reports()

        with reports_tabs[4]:
            self._maintenance_reports()

        with reports_tabs[5]:
            self._advanced_analytics()

    def _general_reports(self):
        """Display general overview reports"""
        st.subheader("📈 التقارير العامة")

        stations = get_all_stations()
        pumps = get_all_pumps()
        tanks = get_all_tanks()
        employees = get_all_employees()
        fuel_types = get_all_fuel_types()

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("إجمالي المحطات", len(stations) if stations else 0)

        with col2:
            st.metric("إجمالي المضخات", len(pumps) if pumps else 0)

        with col3:
            st.metric("إجمالي الخزانات", len(tanks) if tanks else 0)

        with col4:
            st.metric("إجمالي الموظفين", len(employees) if employees else 0)

        with col5:
            st.metric("أنواع الوقود", len(fuel_types) if fuel_types else 0)

    def _sales_reports(self):
        """Display sales reports"""
        st.subheader("⛽ تقارير المبيعات")
        st.info("🔄 سيتم تطوير تقارير المبيعات قريباً")

    def _stations_reports(self):
        """Display stations reports"""
        st.subheader("🏭 تقارير المحطات")
        st.info("🔄 سيتم تطوير تقارير المحطات قريباً")

    def _employees_reports(self):
        """Display employees reports"""
        st.subheader("👥 تقارير الموظفين")
        st.info("🔄 سيتم تطوير تقارير الموظفين قريباً")

    def _maintenance_reports(self):
        """Display maintenance reports"""
        st.subheader("🔧 تقارير الصيانة")
        st.info("🔄 سيتم تطوير تقارير الصيانة قريباً")

    def _advanced_analytics(self):
        """Display advanced analytics"""
        st.subheader("📊 التحليلات المتقدمة")
        st.info("🔄 سيتم تطوير التحليلات المتقدمة قريباً")
