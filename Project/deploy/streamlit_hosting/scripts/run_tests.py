#!/usr/bin/env python3
"""
سكريبت تشغيل الاختبارات - Test Runner Script
سكريبت لتشغيل جميع اختبارات المشروع
"""

import unittest
import sys
import os
from pathlib import Path

# إضافة مسار المشروع إلى sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests():
    """تشغيل جميع الاختبارات"""
    print("🚀 بدء تشغيل اختبارات نظام إدارة محطات الوقود")
    print("=" * 60)

    # اكتشاف جميع الاختبارات
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # مسار مجلد الاختبارات
    tests_dir = project_root / "tests"

    if not tests_dir.exists():
        print(f"❌ مجلد الاختبارات غير موجود: {tests_dir}")
        return False

    # تحميل جميع ملفات الاختبارات
    test_files = list(tests_dir.glob("test_*.py"))

    if not test_files:
        print("⚠️ لم يتم العثور على ملفات اختبارات")
        return False

    print(f"📁 تم العثور على {len(test_files)} ملف اختبار:")
    for test_file in test_files:
        print(f"  • {test_file.name}")

    print("\n" + "=" * 60)

    # تحميل الاختبارات
    for test_file in test_files:
        try:
            module_name = f"tests.{test_file.stem}"
            test_module = __import__(module_name, fromlist=[''])
            tests = test_loader.loadTestsFromModule(test_module)
            test_suite.addTests(tests)
            print(f"✅ تم تحميل الاختبارات من: {test_file.name}")
        except Exception as e:
            print(f"❌ خطأ في تحميل الاختبارات من {test_file.name}: {e}")
            return False

    print(f"\n📊 إجمالي الاختبارات المحملة: {test_suite.countTestCases()}")
    print("=" * 60)

    # تشغيل الاختبارات
    test_runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )

    print("🏃 تشغيل الاختبارات...")
    print("-" * 60)

    result = test_runner.run(test_suite)

    print("\n" + "=" * 60)
    print("📈 نتائج الاختبارات:")
    print(f"  • إجمالي الاختبارات: {result.testsRun}")
    print(f"  • نجح: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  • فشل: {len(result.failures)}")
    print(f"  • أخطاء: {len(result.errors)}")

    if result.failures:
        print(f"\n❌ الاختبارات الفاشلة ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  • {test}")
            print(f"    {traceback.strip()}")

    if result.errors:
        print(f"\n⚠️ أخطاء في الاختبارات ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  • {test}")
            print(f"    {traceback.strip()}")

    success = len(result.failures) == 0 and len(result.errors) == 0

    if success:
        print("\n🎉 جميع الاختبارات نجحت! ✅")
        return True
    else:
        print(f"\n💥 فشل {len(result.failures) + len(result.errors)} اختبار من أصل {result.testsRun}")
        return False

def main():
    """الدالة الرئيسية"""
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ تم إيقاف الاختبارات بواسطة المستخدم")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 خطأ غير متوقع: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()