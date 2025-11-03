#!/usr/bin/env python3
"""
Test script to verify management module imports work correctly
"""

import sys
import os

# Add the Project directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Project'))

try:
    # Test importing the main management module
    from pages.management.main_management_organized import main
    print("✅ Successfully imported main_management_organized")

    # Test importing individual managers
    from pages.management.settings_manager import SettingsManager
    print("✅ Successfully imported SettingsManager")

    from pages.management.addition_manager import AdditionManager
    print("✅ Successfully imported AdditionManager")

    from pages.management.reports_manager import ReportsManager
    print("✅ Successfully imported ReportsManager")

    from pages.management.main_management_orchestrator import ManagementOrchestrator
    print("✅ Successfully imported ManagementOrchestrator")

    # Test importing from __init__
    from pages.management import SettingsManager, AdditionManager, ReportsManager, ManagementOrchestrator
    print("✅ Successfully imported from __init__.py")

    # Test database imports
    from core.database_enhanced import get_all_stations, get_all_employees
    print("✅ Successfully imported database functions")

    print("\n🎉 All imports successful! The organized management system is ready to use.")
    print("\nTo use the system, call main() from main_management_organized.py")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
