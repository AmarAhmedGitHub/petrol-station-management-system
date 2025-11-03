import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_enhanced import view_all_FuelTank_data, get_all_pumps, get_pump_directory
from core.sensor_api import get_sensor_api

print("Testing sensor monitoring data functions...")

try:
    print("\n1. Testing view_all_FuelTank_data()")
    tanks = view_all_FuelTank_data()
    print(f"Success: Retrieved {len(tanks)} tanks")
    if tanks:
        print(f"Sample: {tanks[0]}")
except Exception as e:
    print(f"Error in view_all_FuelTank_data: {str(e)}")
    import traceback
    traceback.print_exc()

try:
    print("\n2. Testing get_all_pumps()")
    pumps = get_all_pumps()
    print(f"Success: Retrieved {len(pumps)} pumps")
    if pumps:
        print(f"Sample: {pumps[0]}")
except Exception as e:
    print(f"Error in get_all_pumps: {str(e)}")
    import traceback
    traceback.print_exc()

try:
    print("\n3. Testing get_pump_directory()")
    directory = get_pump_directory()
    print(f"Success: Retrieved {len(directory)} directory entries")
    if directory:
        print(f"Sample: {directory[0]}")
except Exception as e:
    print(f"Error in get_pump_directory: {str(e)}")
    import traceback
    traceback.print_exc()

try:
    print("\n4. Testing get_sensor_api().get_all_sensor_readings()")
    sensor_api = get_sensor_api()
    readings = sensor_api.get_all_sensor_readings()
    print(f"Success: Retrieved {len(readings)} sensor readings")
    if readings:
        print(f"Sample: {list(readings.items())[0]}")
except Exception as e:
    print(f"Error in get_all_sensor_readings: {str(e)}")
    import traceback
    traceback.print_exc()

print("\nTest completed.")
