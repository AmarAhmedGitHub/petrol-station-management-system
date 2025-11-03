#!/usr/bin/env python3
"""
اختبار تشغيل واجهة الإدارة المُنظمة
"""

import sys
import os
import streamlit as st

# إضافة مجلد Project إلى المسار
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Project'))

def test_run():
    """اختبار تشغيل الواجهة بدون فحص تسجيل الدخول"""
    # محاكاة تسجيل الدخول
    st.session_state.logged_in = True

    # استيراد وتشغيل الواجهة
    try:
        from pages.management.main_management_orchestrator import ManagementOrchestrator
        orchestrator = ManagementOrchestrator()
        orchestrator.show_main_interface()
        print("✅ تم تشغيل واجهة الإدارة بنجاح!")
    except Exception as e:
        print(f"❌ خطأ في تشغيل الواجهة: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_run()
