#!/usr/bin/env python3
"""
Basic test script for the automation system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test basic imports"""
    print("🔧 اختبار الاستيراد الأساسي...")

    try:
        import streamlit as st
        print(f"✅ Streamlit: {st.__version__}")
    except ImportError as e:
        print(f"❌ Streamlit: {e}")
        return False

    try:
        import mysql.connector
        print("✅ MySQL Connector: OK")
    except ImportError as e:
        print(f"❌ MySQL Connector: {e}")
        return False

    try:
        import requests
        print(f"✅ Requests: {requests.__version__}")
    except ImportError as e:
        print(f"❌ Requests: {e}")
        return False

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        print("✅ APScheduler: OK")
    except ImportError as e:
        print(f"❌ APScheduler: {e}")
        return False

    return True

def test_database():
    """Test database connection"""
    print("\n🗄️ اختبار قاعدة البيانات...")

    try:
        from core.database_enhanced import create_enhanced_tables
        create_enhanced_tables()
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 بدء الاختبار الأساسي للنظام")
    print("=" * 50)

    # Test imports
    imports_ok = test_imports()

    # Test database
    db_ok = test_database()

    print("\n" + "=" * 50)
    if imports_ok and db_ok:
        print("🎉 الاختبار الأساسي نجح!")
        print("\n📋 لتشغيل النظام:")
        print("   Windows: START_AUTOMATION.bat")
        print("   أو: streamlit run main_app_automation.py --server.port 8502")
        print("\n📋 للاختبار الكامل:")
        print("   python test_automation.py")
    else:
        print("⚠️ فشل في بعض الاختبارات - راجع السجلات أعلاه")

if __name__ == "__main__":
    main()
