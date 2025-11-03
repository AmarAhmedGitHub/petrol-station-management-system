# TODO: Automated Daily Migration (Reconciliation) Implementation

## Overview
Implement automated reconciliation process every 7.5 hours using PTS2/ATG sensor integration to calculate employee debts based on sold fuel quantity and predetermined prices.

## Steps
- [ ] Update requirements.txt: Add APScheduler==3.10.4
- [ ] Update core/database.py: Add EmployeeDebt and SensorReadings tables, plus related CRUD functions
- [ ] Create core/automation.py: Implement mock sensor reading, reconciliation logic, and APScheduler setup
- [ ] Update pages/management/main_management_employees.py: Add debt viewing and settlement UI
- [ ] Update pages/reports/main_reports_enhanced.py: Add employee debts analytics section
- [ ] Update main app (app.py or main_app_enhanced.py): Import and start scheduler on app startup
- [ ] Install dependencies: Run pip install APScheduler
- [ ] Update database: Run create_tables() to add new tables
- [ ] Test: Manually trigger reconciliation, verify DB updates, check UI
- [ ] Run app: Start with scheduler using START_ENHANCED_SYSTEM.bat
