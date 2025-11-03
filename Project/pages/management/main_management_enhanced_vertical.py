import streamlit as st
import pandas as pd
from core.database_enhanced import (
    get_all_stations, get_all_pumps, get_all_tanks, get_all_employees,
    get_all_fuel_types, get_all_invoices, get_all_supplies,
    add_petrol_station, add_employee, add_fuel_pump, add_fuel_tank,
    get_dashboard_stats
)

def show_management_interface():
    """Display main management interface with vertical sidebar navigation"""
    st.markdown("""
        <style>
        .management-container {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
        }
        .section-header {
            color: #0d6efd;
            font-size: 2rem;
            font-weight: bold;
            margin: 2rem 0 1rem 0;
            text-align: center;
        }
        .sidebar-nav {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        .nav-item {
            display: block;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            background: linear-gradient(45deg, #0d6efd, #0056b3);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s ease;
            border: none;
         """)