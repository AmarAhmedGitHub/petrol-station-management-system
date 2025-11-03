---
description: Repository Information Overview
alwaysApply: true
---

# Petrol Pump Management System Information

## Summary
A comprehensive management system for petrol pumps built with Python and MySQL. The system provides a web-based interface using Streamlit for managing petrol pump operations, including employee management, customer tracking, inventory control, sales reporting, and sensor monitoring.

## Structure
- **Project/**: Main application code with Streamlit UI, database operations, and API services
- **Backend/**: SQL scripts for database creation and queries
- **Design & Architecture/**: System design diagrams and database schema
- **Report/**: Project documentation and reports
- **venv/**: Python virtual environment

## Language & Runtime
**Language**: Python
**Version**: Python 3.13
**Build System**: None (interpreted language)
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- streamlit >= 1.28.0 (Web UI framework)
- mysql-connector-python >= 8.0.33 (Database connector)
- pymysql >= 1.0.0 (MySQL Python client)
- python-dotenv >= 1.0.0 (Environment variable management)
- pandas >= 2.0.0 (Data manipulation)
- flask >= 2.3.0 (API service)
- flask-cors >= 4.0.0 (Cross-origin resource sharing)
- APScheduler == 3.10.4 (Task scheduling)

**Development Dependencies**:
- matplotlib >= 3.7.0 (Data visualization)
- plotly >= 5.15.0 (Interactive visualizations)
- reportlab >= 4.0.0 (PDF generation)

## Build & Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r Project/requirements.txt

# Create database
python Project/create_enhanced_db_complete.py

# Run application
streamlit run Project/main_app.py
```

## API Service
**Framework**: Flask
**Endpoints**:
- `/welcome`: Welcome message and API status
- `/health`: Health check endpoint
- `/api/v1/stations`: Get all active petrol stations

**Run Command**:
```bash
python Project/api_service.py
```

## Testing
**Framework**: Custom test scripts
**Test Location**: `Project/test_*.py` files
**Run Command**:
```bash
python Project/test_basic.py
```

## Database
**Type**: MySQL
**Schema**: 
- FuelTank, Petrolpump, Employee, Customer, Invoice, Tanker
- FuelSupply, PumpDirectory, EmployeePermissions, SensorReadings
**Connection**: Uses environment variables (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)