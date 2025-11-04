"""
Management Module - Organized Management Interfaces

This module provides organized management interfaces for the Petrol Pump Management System,
divided into three main categories:

1. Settings (Configuration) - System settings, fuel types, shifts, etc.
2. Addition (CRUD Operations) - Adding stations, employees, pumps, tanks, etc.
3. Reports (Analytics) - Viewing and analyzing system data

Each category is properly organized with logical code structure and division.
"""

from .settings_manager import SettingsManager
from .addition_manager import AdditionManager
from .reports_manager import ReportsManager
from .main_management_orchestrator import ManagementOrchestrator

__all__ = [
    'SettingsManager',
    'AdditionManager',
    'ReportsManager',
    'ManagementOrchestrator'
]
