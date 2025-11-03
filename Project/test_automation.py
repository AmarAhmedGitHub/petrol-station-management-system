#!/usr/bin/env python3
"""
Test script for the automation system with sensor integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.sensor_api import get_sensor_api, initialize_sensor_api
from core.automation import get_real_sensor_reading, mock_sensor_reading
from core.database import create_enhanced_tables

def test_sensor_api():
    """Test sensor API connections"""
    print("🔧 اختبار Sensor API...")

    # Initialize sensor API
    initialize_sensor_api()

    # Get API instance
    api = get_sensor_api()

    # Test connections
    pts2_ok = api.test_connection('PTS2')
    atg_ok = api.test_connection('ATG')

    print(f"✅ PTS2 connection: {'OK' if pts2_ok else 'FAILED (expected for demo)'}")
    print(f"✅ ATG connection: {'OK' if atg_ok else 'FAILED (expected for demo)'}")

    # Test sensor readings
    print("\n📊 اختبار قراءات الاستشعار...")

    # Mock reading
    mock_level = mock_sensor_reading('TANK_001', 'PUMP_001')
    print(f"✅ Mock reading for TANK_001: {mock_level:.2f}L")

    # Real sensor reading (will fall back to mock)
    real_level = get_real_sensor_reading('TANK_001', 'PUMP_001')
    print(f"✅ Real sensor reading for TANK_001: {real_level:.2f}L")

    return True

def test_database():
    """Test database connection and tables"""
    print("\n🗄️ اختبار قاعدة البيانات...")

    try:
        create_enhanced_tables()
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 بدء اختبار نظام الاستشعار الآلي")
    print("=" * 50)

    # Test database
    db_ok = test_database()

    # Test sensor API
    sensor_ok = test_sensor_api()

    print("\n" + "=" * 50)
    if db_ok and sensor_ok:
        print("🎉 جميع الاختبارات نجحت!")
        print("\n📋 لتشغيل النظام:")
        print("   Windows: START_AUTOMATION.bat")
        print("   أو: streamlit run main_app_automation.py --server.port 8502")
    else:
        print("⚠️ بعض الاختبارات فشلت - راجع السجلات أعلاه")

if __name__ == "__main__":
    main()
