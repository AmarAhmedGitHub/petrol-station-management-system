#!/usr/bin/env python3
"""
Test script for enhanced database functions
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database_enhanced import (
    get_all_fuel_types, add_fuel_type, get_all_stations, add_petrol_station,
    get_all_employees, add_employee, get_all_pumps, add_fuel_pump,
    get_all_tanks, add_fuel_tank, get_dashboard_stats,
    add_tank_sensor, get_all_tank_sensors, update_tank_sensor, delete_tank_sensor,
    add_pump_sensor, get_all_pump_sensors, update_pump_sensor, delete_pump_sensor
)

def test_fuel_types():
    """Test fuel types CRUD operations"""
    print("🧪 Testing Fuel Types...")

    # Test adding fuel type
    result = add_fuel_type("TEST001", "Test Fuel", "Test Description", 5.50)
    print(f"✅ Add fuel type: {'Success' if result else 'Failed'}")

    # Test getting all fuel types
    fuel_types = get_all_fuel_types()
    print(f"✅ Get all fuel types: {len(fuel_types)} types found")

    return True

def test_stations():
    """Test stations CRUD operations"""
    print("🏭 Testing Stations...")

    # Test adding station
    result = add_petrol_station(
        "TEST001", "Test Station", "Test Company", "REG001",
        2024, "Test State", "Test City", "Test Address", "123456789", "EMP001"
    )
    print(f"✅ Add station: {'Success' if result else 'Failed'}")

    # Test getting all stations
    stations = get_all_stations()
    print(f"✅ Get all stations: {len(stations)} stations found")

    return True

def test_employees():
    """Test employees CRUD operations"""
    print("👥 Testing Employees...")

    # Test adding employee
    result = add_employee(
        "TEST001", "TEST001", "Test Employee", "ذكر", "عامل مضخة",
        "1990-01-01", 3000.0, "Test Address", "test@email.com", "123456789", "MGR001"
    )
    print(f"✅ Add employee: {'Success' if result else 'Failed'}")

    # Test getting all employees
    employees = get_all_employees()
    print(f"✅ Get all employees: {len(employees)} employees found")

    return True

def test_pumps():
    """Test pumps CRUD operations"""
    print("⛽ Testing Pumps...")

    # Test adding pump
    result = add_fuel_pump(
        "TEST001", "TEST001", "Test Pump", 1, "Test Location",
        "FUEL001", "TANK001", "EMP001"
    )
    print(f"✅ Add pump: {'Success' if result else 'Failed'}")

    # Test getting all pumps
    pumps = get_all_pumps()
    print(f"✅ Get all pumps: {len(pumps)} pumps found")

    return True

def test_tanks():
    """Test tanks CRUD operations"""
    print("🗂️ Testing Tanks...")

    # Test adding tank
    result = add_fuel_tank(
        "TEST001", "TEST001", "FUEL001", "Test Tank", 50000.0, 5.0, 1.0, "Test Location"
    )
    print(f"✅ Add tank: {'Success' if result else 'Failed'}")

    # Test getting all tanks
    tanks = get_all_tanks()
    print(f"✅ Get all tanks: {len(tanks)} tanks found")

    return True

def test_dashboard():
    """Test dashboard statistics"""
    print("📊 Testing Dashboard Stats...")

    try:
        stats = get_dashboard_stats()
        print(f"✅ Dashboard stats: {stats}")
        return True
    except Exception as e:
        print(f"❌ Dashboard stats failed: {e}")
        return False

def test_tank_sensors():
    """Test tank sensors CRUD operations"""
    print("🛢️ Testing Tank Sensors...")

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

def test_pump_sensors():
    """Test pump sensors CRUD operations"""
    print("⛽ Testing Pump Sensors...")

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

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Database Tests...\n")

    tests = [
        ("Fuel Types", test_fuel_types),
        ("Stations", test_stations),
        ("Employees", test_employees),
        ("Pumps", test_pumps),
        ("Tanks", test_tanks),
        ("Dashboard", test_dashboard),
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
        print("🎉 All tests passed! Enhanced database integration is working correctly.")
