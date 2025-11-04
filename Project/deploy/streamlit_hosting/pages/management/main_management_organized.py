"""
Organized Management Interface - Main Entry Point

This module provides the main entry point for the organized management system,
coordinating all settings, addition, and reports interfaces with proper logic and division.
"""

import streamlit as st
from .main_management_orchestrator import ManagementOrchestrator


def main():
    """Main function for the organized management interface"""
    if not st.session_state.get('logged_in', False):
        st.warning("⚠️ يجب تسجيل الدخول للوصول إلى صفحة الإدارة.")
        return

    # Initialize the management orchestrator
    orchestrator = ManagementOrchestrator()

    # Display the main management interface
    orchestrator.show_main_interface()


if __name__ == "__main__":
    main()
