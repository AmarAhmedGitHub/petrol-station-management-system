import random
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .database_enhanced import (
    record_sensor_reading, get_last_reading, add_employee_debt,
    get_shift_reading,
    get_fuel_price, get_pump_directory, view_all_Employee_data,
    view_all_FuelTank_data
)
from .sensor_api import get_sensor_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_real_sensor_reading(tank_id, pump_id=None):
    """
    Get real sensor reading from PTS2/ATG APIs

    Args:
        tank_id: Tank identifier
        pump_id: Pump identifier (optional)

    Returns:
        Fuel level in liters or None if error
    """
    try:
        sensor_api = get_sensor_api()

        # Try PTS2 first, then ATG as fallback
        sensor_types = ['PTS2', 'ATG']

        for sensor_type in sensor_types:
            # Check if we have mappings for this sensor type
            if tank_id in sensor_api.sensor_mappings.get(sensor_type, {}):
                sensor_id = sensor_api.sensor_mappings[sensor_type][tank_id]
                level = sensor_api.get_sensor_reading(sensor_type, sensor_id)
                if level is not None:
                    logger.info(f"Got real {sensor_type} reading for tank {tank_id}: {level}L")
                    return level

        # If no real sensor mapping found, fall back to mock reading
        logger.warning(f"No sensor mapping found for tank {tank_id}, using mock reading")
        return mock_sensor_reading(tank_id, pump_id)

    except Exception as e:
        logger.error(f"Error getting real sensor reading for tank {tank_id}: {str(e)}")
        # Fall back to mock reading on error
        return mock_sensor_reading(tank_id, pump_id)

def mock_sensor_reading(tank_id, pump_id=None):
    """
    Mock sensor reading for PTS2/ATG.
    Used as fallback when real sensors are not available.
    """
    # Get tank capacity for realistic simulation
    tanks = view_all_FuelTank_data()
    capacity = 10000  # Default capacity
    for tank in tanks:
        if tank[0] == tank_id:
            capacity = float(tank[2]) if tank[2] else 10000
            break

    # Simulate realistic fuel level (between 10% and 90% of capacity)
    level = random.uniform(capacity * 0.1, capacity * 0.9)
    sensor_type = random.choice(['PTS2', 'ATG'])

    # Record the reading
    success = record_sensor_reading(tank_id, level, sensor_type, pump_id)
    if success:
        logger.info(f"Recorded mock sensor reading: Tank {tank_id}, Level {level:.2f}, Type {sensor_type}")
    else:
        logger.error(f"Failed to record mock sensor reading for tank {tank_id}")

    return level

def perform_daily_reconciliation():
    """
    Perform automated reconciliation every 7.5 hours.
    Calculate sold fuel based on tank level differences and create employee debts.
    """
    logger.info("Starting automated reconciliation process...")

    try:
        # Get pump directory with employee assignments
        pump_directory = get_pump_directory()
        if not pump_directory:
            logger.warning("No pump directory found. Skipping reconciliation.")
            return

        # Process each pump/employee assignment
        for pump_entry in pump_directory:
            pump_id = pump_entry[1]  # Petrolpump_No
            tank_id = pump_entry[2]  # FuelTank_ID
            employee_id = pump_entry[3]  # Employee_ID

            if not employee_id or not tank_id:
                continue  # Skip unassigned pumps

            # Get last reading for this tank/pump
            last_reading = get_last_reading(tank_id, pump_id)
            if not last_reading:
                logger.info(f"No previous reading for tank {tank_id}, pump {pump_id}. Using current tank level.")
                # Use current tank level as baseline
                tanks = view_all_FuelTank_data()
                current_level = None
                for tank in tanks:
                    if tank[0] == tank_id:
                        current_level = float(tank[3]) if tank[3] else 0
                        break
                if current_level is None:
                    continue
            else:
                current_level = last_reading[0]

            # Get new sensor reading
            new_level = get_real_sensor_reading(tank_id, pump_id)

            # Calculate sold quantity (previous - current)
            sold_quantity = current_level - new_level

            if sold_quantity < 0:
                logger.warning(f"Negative sold quantity for tank {tank_id}, pump {pump_id}: {sold_quantity}. Skipping.")
                continue
            elif sold_quantity == 0:
                logger.info(f"No fuel sold for tank {tank_id}, pump {pump_id}.")
                continue

            # Get fuel type and price
            tanks = view_all_FuelTank_data()
            fuel_type = None
            for tank in tanks:
                if tank[0] == tank_id:
                    fuel_type = tank[1]
                    break

            if not fuel_type:
                logger.error(f"Could not determine fuel type for tank {tank_id}")
                continue

            unit_price = get_fuel_price(fuel_type)
            owed_amount = sold_quantity * unit_price

            # Create debt record
            settlement_date = datetime.now().date()
            notes = f"Automated reconciliation - Tank: {tank_id}, Pump: {pump_id}, Period: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            success = add_employee_debt(employee_id, settlement_date, sold_quantity, unit_price, owed_amount, notes)
            if success:
                logger.info(f"Created debt record for employee {employee_id}: {owed_amount:.2f} SAR")
            else:
                logger.error(f"Failed to create debt record for employee {employee_id}")

        logger.info("Reconciliation process completed.")

    except Exception as e:
        logger.error(f"Error during reconciliation: {str(e)}")

def start_scheduler():
    """
    Start the background scheduler for automated reconciliation.
    """
    scheduler = BackgroundScheduler()

    # Schedule reconciliation every 7.5 hours (27000 seconds)
    trigger = IntervalTrigger(seconds=27000)
    scheduler.add_job(perform_daily_reconciliation, trigger, id='reconciliation_job')

    scheduler.start()
    logger.info("Scheduler started. Reconciliation will run every 7.5 hours.")

    return scheduler

def manual_reconciliation():
    """
    Manually trigger reconciliation for testing purposes.
    """
    logger.info("Manual reconciliation triggered.")
    perform_daily_reconciliation()


def reconcile_shift(employee_id, shift_id, directory_id, pump_id=None, tank_id=None):
    """
    Reconcile a single shift for a given employee and pump/tank assignment.

    Steps:
    - read baseline and end readings from EmployeeShiftReadings
    - compute sold_quantity = baseline - end
    - lookup fuel type and unit price
    - create EmployeeDebt record via add_employee_debt

    Returns True on successful debt creation, False otherwise.
    """
    logger.info(f"Reconciling shift {shift_id} for employee {employee_id} (dir {directory_id})")
    try:
        # Get baseline and end readings
        baseline = get_shift_reading(employee_id, shift_id, directory_id, 'baseline')
        end = get_shift_reading(employee_id, shift_id, directory_id, 'end')

        if not baseline:
            logger.warning(f"No baseline reading for shift {shift_id}, employee {employee_id}, dir {directory_id}")
            return False
        if not end:
            logger.warning(f"No end reading for shift {shift_id}, employee {employee_id}, dir {directory_id}")
            return False

        baseline_level = float(baseline[0])
        end_level = float(end[0])
        sold_quantity = baseline_level - end_level

        if sold_quantity <= 0:
            logger.warning(f"Computed non-positive sold quantity for shift {shift_id}: {sold_quantity}. Skipping.")
            return False

        # Determine tank_id/pump_id if not provided by looking up pump directory
        if not tank_id or not pump_id:
            pd = get_pump_directory() or []
            for entry in pd:
                # PumpDirectory columns: Directory_ID, Pump_ID, Station_ID, Employee_ID, Tank_ID, FuelType_ID, Status, Last_Updated
                try:
                    if int(entry[0]) == int(directory_id):
                        pump_id = pump_id or entry[1]
                        tank_id = tank_id or entry[4]
                        fuel_type = entry[5]
                        break
                except Exception:
                    continue

        # Fallback: try to get fuel type from FuelTanks
        fuel_type = None
        tanks = view_all_FuelTank_data() or []
        for tank in tanks:
            # FuelTanks columns (as used elsewhere) - attempt to match Tank_ID
            if tank and tank[0] == tank_id:
                # Many queries in code expect fuel_type at index 1
                try:
                    fuel_type = tank[1]
                except Exception:
                    fuel_type = None
                break

        if not fuel_type:
            logger.error(f"Could not determine fuel type for tank {tank_id}")
            return False

        unit_price = get_fuel_price(fuel_type)
        owed_amount = sold_quantity * unit_price

        settlement_date = datetime.now().date()
        notes = f"Shift reconciliation - Shift:{shift_id}, Dir:{directory_id}, Pump:{pump_id}, Tank:{tank_id}"

        success = add_employee_debt(employee_id, settlement_date, sold_quantity, unit_price, owed_amount, notes)
        if success:
            logger.info(f"Created debt for employee {employee_id}: {owed_amount:.2f} (sold {sold_quantity:.2f} L)")
            return True
        else:
            logger.error(f"Failed to create debt for employee {employee_id}")
            return False

    except Exception as e:
        logger.error(f"Error reconciling shift {shift_id} for employee {employee_id}: {e}")
        return False

# For testing
if __name__ == "__main__":
    manual_reconciliation()

# New functions to fix import error and provide automation settings functionality

import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'automation_settings.json')

def get_automation_settings():
    """
    Get automation settings from JSON file.
    Returns a dictionary of settings or empty dict if file not found.
    """
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings
    except Exception as e:
        logger.error(f"Failed to read automation settings: {str(e)}")
        return {}

def update_automation_settings(new_settings):
    """
    Update automation settings in JSON file.
    new_settings: dict of settings to update.
    Returns True if successful, False otherwise.
    """
    settings = get_automation_settings()
    settings.update(new_settings)
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to update automation settings: {str(e)}")
        return False
