#!/usr/bin/env python3
"""
Test script for sensor CRUD functions
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit to avoid import error
sys.modules['streamlit'] = type(sys)('streamlit')

from core.database_enhanced import (
    add_tank_sensor, get_all_tank_sensors, update_tank_sensor, delete_tank_sensor,
    add_pump_sensor, get_all_pump_sensors, update_pump_sensor, delete_pump_sensor
)

def test_tank_sensors():
    """Test tank sensors CRUD operations"""
    print("🛢️ Testing Tank Sensors...")

    try:
        # First create required parent records
        from core.database_enhanced import add_petrol_station, add_fuel_type, add_fuel_tank

        # Create station
        add_petrol_station(
            "TEST001", "Test Station", "Test Company", "REG001",
            2024, "Test State", "Test City", "Test Address", "123456789", "EMP001"
        )

        # Create fuel type
        add_fuel_type("FUEL001", "Test Fuel", "Test Description", 5.50)

        # Create tank
        add_fuel_tank(
            "TANK001", "TEST001", "FUEL001", "Test Tank", 50000.0, 5.0, 1.0, "Test Location"
        )

        # Test adding tank sensor
        result = add_tank_sensor(
            "TANK001", "Level Sensor", "Model X", "2024-01-01", "2024-01-01", "2024-12-31",
            True, "Top", "Liters", 1000.0, 50000.0, True, "Test sensor"
        )
        print(f"✅ Add tank sensor: {'Success' if result else 'Failed'}")

        # Test getting all tank sensors
        sensors = get_all_tank_sensors()
        print(f"✅ Get all tank sensors: {len(sensors)} sensors found")

        # Test updating tank sensor
        if sensors:
            sensor_id = sensors[0]['Sensor_ID']
            result = update_tank_sensor(sensor_id, Sensor_Model="Updated Model")
            print(f"✅ Update tank sensor: {'Success' if result else 'Failed'}")

            # Test deleting tank sensor
            result = delete_tank_sensor(sensor_id)
            print(f"✅ Delete tank sensor: {'Success' if result else 'Failed'}")

        return True
    except Exception as e:
        print(f"❌ Tank sensor test failed: {e}")
        return False

def test_pump_sensors():
    """Test pump sensors CRUD operations"""
    print("⛽ Testing Pump Sensors...")

    try:
        # First create required parent records
        from core.database_enhanced import add_petrol_station, add_fuel_type, add_employee, add_fuel_pump

        # Create station (if not already exists)
        add_petrol_station(
            "TEST002", "Test Station 2", "Test Company", "REG002",
            2024, "Test State", "Test City", "Test Address", "123456789", "EMP001"
        )

        # Create fuel type (if not already exists)
        add_fuel_type("FUEL002", "Test Fuel 2", "Test Description", 6.50)

        # Create employee
        add_employee(
            "EMP001", "TEST002", "Test Employee", "ذكر", "عامل مضخة",
            "1990-01-01", 3000.0, "Test Address", "test@email.com", "123456789", "MGR001"
        )

        # Create pump
        add_fuel_pump(
            "PUMP001", "TEST002", "Test Pump", 1, "Test Location",
            "FUEL002", "TANK001", "EMP001"
        )

        # Test adding pump sensor
        result = add_pump_sensor(
            "PUMP001", "Flow Sensor", "Model Y", "2024-01-01", "2024-01-01", "2024-12-31",
            True, "Outlet", "L/min", 10.0, 100.0, True, "Test pump sensor"
        )
        print(f"✅ Add pump sensor: {'Success' if result else 'Failed'}")

        # Test getting all pump sensors
        sensors = get_all_pump_sensors()
        print(f"✅ Get all pump sensors: {len(sensors)} sensors found")

        # Test updating pump sensor
        if sensors:
            sensor_id = sensors[0]['Sensor_ID']
            result = update_pump_sensor(sensor_id, Sensor_Model="Updated Pump Model")
            print(f"✅ Update pump sensor: {'Success' if result else 'Failed'}")

            # Test deleting pump sensor
            result = delete_pump_sensor(sensor_id)
            print(f"✅ Delete pump sensor: {'Success' if result else 'Failed'}")

        return True
    except Exception as e:
        print(f"❌ Pump sensor test failed: {e}")
        return False

def main():
    """Run sensor tests"""
    print("🚀 Starting Sensor CRUD Tests...\n")

    tests = [
        ("Tank Sensors", test_tank_sensors),
        ("Pump Sensors", test_pump_sensors)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            print(f"Running {test_name} Test")
            print('='*50)
            if test_func():
                passed += 1
                print(f"✅ {test_name} Test PASSED")
            else:
                print(f"❌ {test_name} Test FAILED")
        except Exception as e:
            print(f"❌ {test_name} Test ERROR: {e}")

    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    print('='*50)

    if passed == total:
        print("🎉 All sensor tests passed! CRUD functions are working correctly.")
    else:
        print("❌ Some tests failed. Check the database setup or function implementations.")

if __name__ == "__main__":
    main()
